import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
from tkinter import font

#透過 TMDb API 取得電影資訊
def get_movie_info(movie_name,api_key):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_name}&language=zh-TW"
        response = requests.get(url)
        response.raise_for_status()  # 處理異常
        return response.json()
    except Exception as e:
        messagebox.showerror("錯誤", f"無法取得電影資訊: {e}")
        return None
    
#開新視窗
def open_new_window():
    new_window = tk.Toplevel(root)
    new_window.title("電影搜尋結果")  

    # 設定新視窗的位置和大小
    new_window.geometry("500x900+{}+{}".format(root.winfo_x() + root.winfo_width(), root.winfo_y()))
    
    # 顯示查詢結果的標籤
    result_label = tk.Label(new_window, text="", justify="left", anchor="w", wraplength=450,font = noto_font)
    result_label.pack(pady=10)

    #顯示完整電影簡介的按鈕
    show_overview_button = tk.Button(new_window, text="顯示完整簡介", font=noto_font)
    show_overview_button.pack(pady=5)
    
    # 顯示電影海報的標籤
    poster_label = tk.Label(new_window)
    poster_label.pack(pady=10)
       
    return new_window, result_label, show_overview_button,poster_label

# 顯示電影片名選項
def show_movie_options(movies):
    listbox.delete(0, tk.END)  # 清空現有選項
    
    for movie in movies:
        listbox.insert(tk.END, movie['title'])
    
    listbox_frame.pack(pady=10)  
    
# 顯示電影資訊
def display_selected_movie():
    selected_index = listbox.curselection()  # 取得被選中的索引
    
    #如果未選取，跳出警告
    if not selected_index:
        messagebox.showwarning("選擇錯誤", "請選擇一部電影")
        return
    
    selected_movie = current_movies[selected_index[0]]  # 根據索引選取電影
    
    try:
        if selected_movie:
        
            # 呼叫 open_new_window 函式來開啟新視窗
            new_window, result_label, show_overview_button, poster_label = open_new_window()
        
            keys_to_display = ['title','original_title', 'release_date','original_language','overview' ,'vote_average', 'vote_count']
        
            labels = {  "title": "中文片名",
                    "original_title":  "原文片名",
                    "release_date": "上映日期",
                    "original_language": "語言",
                    "overview": "簡介",
                    "vote_average": "評分",
                    "vote_count": "評價數",
                    "overview2": "完整簡介"
                    }
        
            result_text = ""
        
            for key in keys_to_display:
                if key in selected_movie:
                    if key != "overview" and key != "overview2":
                        result_text += f"{labels[key]}:{selected_movie[key]}\n"
                    elif key == "overview":
                        overview = selected_movie['overview']
                        if len(overview) > 100:  # 簡介縮短
                            short_overview = overview[:100] + "..."
                            result_text += f"{labels[key]}:{short_overview}\n"
                        else:
                            short_overview = overview
                            result_text += f"{labels[key]}:{short_overview}\n"
                    elif key == "overview2":
                        result_text += f"{labels[key]}:{selected_movie['overview']}\n"
                else:
                    result_text += f"{labels[key]}: {selected_movie[key]}\n"
        
            #print(result_text)
            result_label.config(text=result_text)
        
            if selected_movie['overview']:
                show_overview_button.config(command=lambda: show_full_overview(selected_movie['overview']))             

            if selected_movie.get('poster_path'):  # 檢查是否有海報資料
                poster_url = f"https://image.tmdb.org/t/p/w500{selected_movie['poster_path']}"
                load_poster_in_window(poster_url, poster_label)  
            else:
                poster_label.config(text="無海報圖片")
            
        else:
            messagebox.showwarning("錯誤", "找不到相關電影資訊，請再試一次。")
    except Exception as e:
        messagebox.showerror("錯誤", f"顯示電影資訊時出錯: {e}")

# 定義搜尋電影的按鈕事件處理函式
def search_movie():
    movie_name = entry.get() # 取得使用者輸入的電影名稱
    
    if not movie_name:
        messagebox.showwarning("輸入錯誤", "請輸入電影名稱")
        return

    data = get_movie_info(movie_name, api_key)
    
    
    if data["results"]:
        global current_movies
        current_movies = data["results"]
        show_movie_options(current_movies)
            
    else:
        messagebox.showwarning("查詢結果", "找不到相關電影資訊，請再試一次")
        
# 定義載入海報圖片的函式        
def load_poster_in_window(url, poster_label):
    try:
        response = requests.get(url)
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img = img.resize((300, 450), Image.Resampling.LANCZOS)
    
        photo = ImageTk.PhotoImage(img)
        poster_label.config(image=photo)
        poster_label.image = photo
    except Exception as e:
        poster_label.config(text=f"無法載入海報: {e}")
        
# 顯示完整簡介的對話框
def show_full_overview(overview):
    try:
        overview_window = tk.Toplevel(root)
        overview_window.title("完整簡介")  
    
        text_widget = tk.Text(overview_window, wrap="word", font=noto_font, height=15, width=60)
        text_widget.pack(padx=10, pady=10)
    
        text_widget.insert(tk.END, overview)
        text_widget.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showerror("錯誤", f"顯示完整簡介時出錯: {e}")
        
#api key
api_key = "e824fdd6b821e1270910c2f708356781"

# 建立主視窗
root = tk.Tk()
root.title("電影資訊查詢")
#root.geometry("550x1000")

# 設定字型 (Noto Sans TC 是支援繁體中文的字型)
noto_font = font.Font(family="Microsoft JhengHei")
label_bold_font = font.Font(family="Microsoft JhengHei",size=15,weight="bold")
button1_font = font.Font(family="Microsoft JhengHei",size=13,weight="bold")

# 建立一個框架，用於包裝所有的控件
frame = tk.Frame(root)
frame.pack(padx=10,pady=10)

# 標籤，用於提示使用者輸入電影名稱
tk.Label(frame, text="請輸入電影名稱:",font = label_bold_font).pack(pady=5)
entry = tk.Entry(frame, width=20,font=noto_font)
entry.pack(pady=10)

# 查詢按鈕，當按下時會觸發 search_movie 函式
tk.Button(frame, text="查詢", command=search_movie,font = button1_font).pack(pady=10)

# 標籤，用於提示使用者選擇電影
tk.Label(frame, text="請選擇電影",font = button1_font).pack()

# 建立一個新框架來放置 Listbox 和選取按鈕
listbox_frame = tk.Frame(frame)
listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE, font=noto_font, width=50, height=5)
listbox.pack(padx=5)
select_button = tk.Button(listbox_frame, text="顯示選定電影資訊", command=display_selected_movie, font=noto_font)
select_button.pack(padx=5,pady=10)
listbox_frame.pack(pady=10)  


# 啟動主事件迴圈
root.mainloop()   
