"""
Database operations for the Barcode Printer Application
"""
import mysql.connector
from mysql.connector import Error, pooling
from typing import List, Dict, Optional
import config
from utils import log_event
import settings_manager

class DatabaseManager:
    """Handles all database interactions"""
    
    def __init__(self):
        """Initialize database connection pool"""
        self.db_config = settings_manager.load_db_settings()
        self.connection = None
        self.pool = None
        
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="mypool",
                pool_size=5,
                **self.db_config
            )
            log_event("Database connection pool initialized")
        except Error as e:
            log_event(f"Error initializing connection pool: {e}", 'error')
            # Don't raise here, allow app to start even if DB is down, 
            # so user can change settings
    
    def get_connection(self):
        """Get a connection from the pool"""
        if not self.pool:
             raise Error("Connection pool not initialized")
             
        try:
            return self.pool.get_connection()
        except Error as e:
            log_event(f"Error getting connection: {e}", 'error')
            raise
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute a SELECT query and return results as list of dictionaries"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            return results
        
        except Error as e:
            log_event(f"Database query error: {e}", 'error')
            return []
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def get_semesters(self) -> List[Dict]:
        """Fetch all semesters from timetable_semester table"""
        query = """
            SELECT * FROM timetable_semester 
            ORDER BY EntryID DESC
        """
        try:
            semesters = self.execute_query(query)
            log_event(f"Retrieved {len(semesters)} semesters")
            return semesters
        except Exception as e:
            log_event(f"Error fetching semesters: {e}", 'error')
            return []
    
    def get_modules_by_semester(self, semester_code: str) -> List[Dict]:
        """Fetch module codes from exam_timetable_hall for a given semester code"""
        query = """
            SELECT DISTINCT ModuleCode 
            FROM exam_timetable_hall 
            WHERE SemesterCode = %s
            ORDER BY ModuleCode
        """
        try:
            modules = self.execute_query(query, (semester_code,))
            log_event(f"Retrieved {len(modules)} modules for semester {semester_code}")
            return modules
        except Exception as e:
            log_event(f"Error fetching modules: {e}", 'error')
            return []
    
    def get_module_name(self, module_code: str) -> Optional[str]:
        """Call getmodulename MySQL function to get module name"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Call the MySQL function
            cursor.execute("SELECT getmodulename(%s) as module_name", (module_code,))
            result = cursor.fetchone()
            
            if result and result[0]:
                module_name = result[0]
                log_event(f"Retrieved module name for {module_code}: {module_name}")
                return module_name
            else:
                log_event(f"No module name found for {module_code}", 'warning')
                return None
        
        except Error as e:
            log_event(f"Error calling getmodulename function: {e}", 'error')
            return None
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def get_barcode_data(self, module_code: str, semester_code: str) -> List[Dict]:
        """Fetch barcode data from exam_barcode table for students in this module/semester"""
        query = """
            SELECT eb.*, tv.VenueName
            FROM exam_barcode eb
            JOIN exam_timetable_hall eth ON eb.ExamHallID = eth.EntryID
            JOIN timetable_venue tv ON eth.VenueID = tv.EntryID
            WHERE eth.ModuleCode = %s AND eth.SemesterCode = %s
            ORDER BY eb.SeatNo
        """
        try:
            results = self.execute_query(query, (module_code, semester_code))
            if results:
                log_event(f"Retrieved {len(results)} barcode records for module {module_code}")
                return results
            else:
                log_event(f"No barcode data found for module {module_code}", 'warning')
                return []
        except Exception as e:
            log_event(f"Error fetching barcode data: {e}", 'error')
            return []
    
    def get_exam_dates(self, semester_code: str) -> List[str]:
        """Fetch distinct exam dates for a semester"""
        query = """
            SELECT DISTINCT ExamDate 
            FROM exam_timetable 
            WHERE SemesterCode = %s 
            ORDER BY ExamDate
        """
        try:
            results = self.execute_query(query, (semester_code,))
            dates = [row['ExamDate'] for row in results if row['ExamDate']]
            log_event(f"Retrieved {len(dates)} exam dates for {semester_code}")
            return dates
        except Exception as e:
            log_event(f"Error fetching exam dates: {e}", 'error')
            return []

    def get_modules_by_date(self, exam_date: str, semester_code: str) -> List[Dict]:
        """Fetch modules scheduled for a specific date and semester"""
        # Join exam_timetable to filter by date, then get modules
        query = """
            SELECT DISTINCT eth.ModuleCode 
            FROM exam_timetable_hall eth
            JOIN exam_timetable et ON eth.ModuleCode = et.ModuleCode 
                AND eth.SemesterCode = et.SemesterCode
            WHERE et.ExamDate = %s AND eth.SemesterCode = %s
            ORDER BY eth.ModuleCode
        """
        try:
            modules = self.execute_query(query, (exam_date, semester_code))
            log_event(f"Retrieved {len(modules)} modules for date {exam_date}")
            return modules
        except Exception as e:
            log_event(f"Error fetching modules by date: {e}", 'error')
            return []

    def get_student_by_barcode(self, barcode: str) -> Optional[Dict]:
        """Fetch student and exam details by barcode"""
        # We need to join multiple tables to get full exam details
        # exam_barcode -> exam_timetable_hall -> timetable_venue
        #                                     -> exam_timetable (for date/time if needed)
        query = """
            SELECT 
                eb.StudentID, eb.SeatNo, eb.StudentLevel,
                tv.VenueName, 
                eth.ModuleCode, eth.SemesterCode,
                et.ExamDate, etd.EndTime as StartTime -- Assuming StartTime/EndTime in detail?
            FROM exam_barcode eb
            JOIN exam_timetable_hall eth ON eb.ExamHallID = eth.EntryID
            JOIN timetable_venue tv ON eth.VenueID = tv.EntryID
            LEFT JOIN exam_timetable et ON eth.ModuleCode = et.ModuleCode 
                AND eth.SemesterCode = et.SemesterCode
            LEFT JOIN exam_timetable_detail etd ON et.EntryID = etd.ExamTimetableID
            WHERE eb.Barcode = %s
            LIMIT 1
        """
        # Note: exam_timetable_detail join might be tricky without knowing FK. 
        # Assuming simple flow for now. If detail join fails, we'll refine.
        # Actually, let's stick to known tables to avoid complex joins breaking.
        
        query_safe = """
            SELECT 
                eb.StudentID, eb.SeatNo, eb.StudentLevel, eb.Barcode,
                tv.VenueName, 
                eth.ModuleCode
            FROM exam_barcode eb
            JOIN exam_timetable_hall eth ON eb.ExamHallID = eth.EntryID
            JOIN timetable_venue tv ON eth.VenueID = tv.EntryID
            WHERE eb.Barcode = %s OR eb.StudentID = %s
            LIMIT 1
        """
        try:
            results = self.execute_query(query_safe, (barcode, barcode))
            if results:
                return results[0]
            return None
        except Exception as e:
            log_event(f"Error fetching student by barcode: {e}", 'error')
            return None

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            connection = self.get_connection()
            if connection.is_connected():
                connection.close()
                log_event("Database connection test successful")
                return True
            return False
        except Error as e:
            log_event(f"Database connection test failed: {e}", 'error')
            return False

    def validate_user(self, email: str) -> tuple[bool, str]:
        """Validate user email against authorized users"""
        try:
            # Check config first
            if email in config.AUTHORIZED_USERS:
                log_event(f"User validated: {email}")
                return True, None
            
            # If we wanted to check a DB table, we would do it here.
            # For now, rely on strict config list.
            log_event(f"Unauthorized login attempt: {email}", 'warning')
            return False, "User not authorized"
        except Exception as e:
            log_event(f"Error validating user: {e}", 'error')
            return False, f"Validation error: {str(e)}"
