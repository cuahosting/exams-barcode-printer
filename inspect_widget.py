from ttkbootstrap.widgets.scrolled import ScrolledText
import ttkbootstrap as ttk

def inspect():
    app = ttk.Window()
    st = ScrolledText(app)
    print("ScrolledText dir:", dir(st))
    try:
        st.configure(state='disabled')
        print("Direct configure state works")
    except Exception as e:
        print(f"Direct configure failed: {e}")
        
    if hasattr(st, 'text'):
        print("Has .text attribute")
        try:
            st.text.configure(state='disabled')
            print(".text configure state works")
        except Exception as e:
            print(f".text configure failed: {e}")
            
    app.destroy()

if __name__ == "__main__":
    inspect()
