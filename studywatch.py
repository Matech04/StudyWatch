import customtkinter as ct
import time as t
import threading
import sqlite3 as sql
import datetime 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class App(ct.CTk):
    
  def __init__(self):
    super().__init__()

    #Database
    self.conn = sql.connect('studywatch.db', check_same_thread=False)
    self.cursor = self.conn.cursor()

    self.cursor.execute('''
    CREATE TABLE IF NOT EXISTS studywatch (
        id INTEGER PRIMARY KEY,
        date DATE,
        hour INTEGER
        )
    ''')
    self.conn.commit()
  
    #Graphics Settings
    self.title("StudyWatch")
    self.geometry("500x800")
    ct.set_appearance_mode("System")
    ct.set_default_color_theme("dark-blue")
    self.grid_columnconfigure(0, weight=1)
    self.grid_rowconfigure(0, weight=0)

    #Calculations Settings/Variables
    self.is_counting = False
    self.restart = False

    #App Name
    self.label = ct.CTkLabel(self, text="StudyWatch", font=("Roboto", 40))
    self.label.grid(row=0 , column= 0, padx=20 , pady=20 ,sticky="ew")

    #TimeBox Rząd pierwszy to ma sie zamieniać na odliczanie czasu
    self.timebox_entry = IntSpinbox(self)
    self.timebox_entry.grid(row=1, column=0, pady=15)
    #TimeBox wyświetlanie
    self.timebox_view = ct.CTkLabel(self, text="00:00:00",font=("Roboto", 40))
    #self.timebox_view.grid(row=1, column=0, pady=15)

    #Controlls Buttons Frame
    self.controlls_frame = ct.CTkFrame(self)
    self.controlls_frame.grid(row=2, column=0)
    #Confirm Button
    self.confirm = ct.CTkButton(self.controlls_frame, text="Start" , font=("Roboto", 40), command=self.TimerActivation)
    self.confirm.grid(row=0,column=0,pady=5)
    #Pause Button 
    self.pause = ct.CTkButton(self.controlls_frame, text="Pause" , font=("Roboto", 40), command=self.PauseActivation)
    #Restart
    self.restart_button = ct.CTkButton(self.controlls_frame, text="Restart",font=("Roboto", 40), command=self.RestartActivation)
    self.restart_button.grid(row=0, column=1, pady=5)

    #Sessions Today
    self.sessions_label = ct.CTkLabel(self, text=(f"Session's done today: {self.GetSessionsCount(date=self.Today())}"), font=("Roboto", 40) )
    self.sessions_label.grid(row=3, column = 0)

    #Statistics
    self.cursor.execute('SELECT date, hour FROM studywatch')
    results = self.cursor.fetchall()

  def CalculateSession(self):
    timer_value = self.timebox_entry.get() * 60
    if timer_value <= 0:
      return[]
    
    segments = []
    while timer_value >= 30*60:
      segments.append(25*60)
      segments.append(5*60)
      timer_value -= 30*60

    if timer_value > 0:
      segments.append(timer_value)

    return segments
  
  def Today(self):
    return datetime.date.today().strftime('%Y-%m-%d')

  def Hour(self):
    return datetime.datetime.now().time().strftime('%H:%M')


  def AddSession(self):
    self.hour = datetime.datetime.now().time()
    self.cursor.execute('INSERT INTO studywatch (date, hour) VALUES (?, ?)', (self.Today(), self.Hour()))
    self.conn.commit()

  def GetSessionsCount(self, date):
    self.cursor.execute('SELECT COUNT(*) FROM studywatch WHERE date = ?', (date,))
    pom_count = self.cursor.fetchone()[0]
    return pom_count

  def GetDates(self):
    self.cursor.execute('SELECT DISTINCT date FROM studywatch')
    dates_with_sessions = [row[0]for row in self.cursor.fetchall()]
    return dates_with_sessions
  
  def CheckStatistics(self):
    self.cursor.execute('SELECT date, hour FROM studywatch')
    results = self.cursor.fetchall()

    dates = [result[0] for result in results]
    hours = [result[1] for result in results]

    plt.figure(figsize=(10, 6))
    plt.plot(dates, hours, marker='o', linestyle='-')
    plt.title('Studywatch Stats')
    plt.xlabel('Data')
    plt.ylabel('Session Time')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()



  def TimerActivation(self):
    timer_value = self.timebox_entry.get()
    if timer_value >= 1:
      self.GoToTimer()
      self.timer = threading.Thread(target=self.Timer2,args=(self.CalculateSession(),))
      self.timer.start()

  def PauseActivation(self):
    threading.Thread(target=self.Pause).start()

  def RestartActivation(self):
    threading.Thread(target=self.Restart).start()

  def Timer2(self, segments):
    stages = ["Learning", "Break"]
    stage = stages[0]
    print (segments)


    for time in segments:
      print(time), print(segments)
      self.is_counting = True
      self.label.configure(text=stage)

      while time >= 0:

        seconds = time % 60
        minutes = int(time / 60) % 60
        hours = int(time / 3600)

        self.timebox_view.configure(text=(f"{hours:02}:{minutes:02}:{seconds:02}"))
        t.sleep(1)
        print(self.is_counting)

        if self.is_counting ==True:
          time -=1
          print(time)
        
        if time == -1:
          print("Stage Finished")

          if stage == stages[0]:
            self.AddSession()
            self.sessions_label.configure(text=(f"Session's done today: {self.GetSessionsCount(self.Today())}"))
            stage = stages[1]
            break
          if stage == stages[1]:
            stage = stages[0]
            break

        if self.restart ==True:
          break
      if self.restart ==True:
          self.restart = False
          break
      
    self.GoToEntry()
  
  def Pause(self):
    if self.is_counting == True: 
      self.is_counting = False 
    else: 
      self.is_counting = True

  def Restart(self):
    self.Pause()
    self.restart = True


  def GoToEntry(self):
    print("Going to Entry")
    self.label.configure(text="StudyWatch")
    self.timebox_view.grid_remove()
    self.timebox_entry.grid(row=1, column=0, pady=15)
    self.pause.grid_remove()
    self.confirm.grid(row=0,column=0,pady=5)

  
  def GoToTimer(self):
    print("Going To Timer")
    self.timebox_entry.grid_remove()
    self.timebox_view.grid(row=1, column=0, pady=15)
    self.confirm.grid_remove()
    self.pause.grid(row=0,column=0,pady=5)

    
      
  

class IntSpinbox(ct.CTkFrame):


  def __init__(self, master, step_size: int = 5, min_height: int = 60):
    super().__init__(master)

    self.step_size = step_size
    self.min_height = min_height / 2

    #Entry
    self.entry = ct.CTkEntry(master=self, justify="center", font=("Roboto", 40), height=min_height)
    self.entry.grid(row=0,column=0, sticky="nsew", columnspan=2, rowspan=2)
    self.entry.insert(0, "0")
    #Add Button
    self.add_button = ct.CTkButton(master=self, text="+" , command=self.add_button_command , height=min_height, width=min_height)
    self.add_button.grid(row=0, column=2, sticky="nsew")
    #Subtract Button
    self.subtract_button = ct.CTkButton(master=self, text="-" , command=self.subtract_button_command , height=min_height, width=min_height)
    self.subtract_button.grid(row=1, column=2, sticky="nsew")

    self.columnconfigure(0, weight=1)

  def subtract_button_command(self):
    try:
      value = int(self.entry.get()) - self.step_size
      if value >= 0:
        self.entry.delete(0, "end")
        self.entry.insert(0, value)
    except ValueError:
      return

  def add_button_command(self):
     try:
      value = int(self.entry.get()) + self.step_size
      self.entry.delete(0, "end")
      self.entry.insert(0, value)
     except ValueError:
      return
     
  def get(self)-> int: 
    try:
      return int(self.entry.get())
    except ValueError:
      set(0)
      return 0
    
  def set(self, value: int):
    self.entry.delete(0, "end")
    self.entry.insert(0, str(int(value)))

if __name__ == "__main__":
    app = App()
    app.mainloop()

