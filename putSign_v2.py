import tkinter as tk
import base64
import cv2
import numpy as np
from tkinter import *
from tkinter import ttk
from pdf2image import convert_from_path
from tkinter.filedialog import askopenfile, asksaveasfilename
from tkinter import messagebox

import os
from PIL import Image, ImageTk, ImageOps


window = tk.Tk()
sw = window.winfo_screenwidth()
sh = window.winfo_screenheight()
window.geometry("%dx%d"%(sw,sh))
window.title("Insert Signature")


x = 0
y = 0
zoom = 0.0
i=0
num = 0

pgh = 0
pgw = 0

pages = []
page_height = sh*0.865

sgw = int(0.15*sw*(1+zoom))
sgh = int(0.15*sh*(1+zoom))

slw = sgw
slh = sgh

img = None
sign = None
 
def nextPage():
	global i
	if (i+1<num):
		i=i+1
		showImg(i)
def prevPage():
	global i
	if (i>0):
		i=i-1
		showImg(i)

def call_blend():
	global i
	blend(i)

def savePdf():
	filename = asksaveasfilename(defaultextension=".pdf",initialfile="myFile.pdf",title="Save",initialdir="/")
	if filename is None:
		return
	pages[0].save(filename, "PDF" ,resolution=100.0, save_all=True, append_images=pages[1:])
	messagebox.showinfo("Successful","Signature Added and Saved Successfully!!")

def blend(i):
	global pages
	if(len(pages)==0):
		messagebox.showerror("Document not found","You have not selected any PDF to put signature into!")
	elif(sign == None):
		messagebox.showerror("Document not found","You have not selected any signature to put into PDF!")
	pageh = pages[i].height
	pagew = pages[i].width
	pages[i].save("doc.jpg")
	signh = 0.15*sh*(1+zoom)*pages[i].height/sh
	signw = 0.15*sw*(1+zoom)*pages[i].height/pgh
	imdoc = cv2.imread("doc.jpg")
	sign_img = sign.resize((int(signw),int(signh)))
	if sign_img.mode in ("RGBA", "P"):
		sign_img = sign_img.convert("RGB")
	sign_img.save("sign_img.jpg")
	imSign = cv2.imread("sign_img.jpg")
	imdoc_portion = imdoc[int((pageh-signh)*int(y)/100):int((pageh-signh)*int(y)/100)+int(signh),int((pagew-signw)*int(x)/100):int((pagew-signw)* int(x)/100)+int(signw)]	
	for r in range(int(signh)):
		for c in range(int(signw)):
			if(imSign[r][c][0]<150 or imSign[r][c][1]<150 or imSign[r][c][2]<150):
				imdoc_portion[r][c] = imSign[r][c]
			else:
				imdoc_portion[r][c] = imdoc_portion[r][c]
	
	imdoc[int((pageh-signh)*int(y)/100):int((pageh-signh)*int(y)/100)+int(signh),int((pagew-signw)*int(x)/100):int((pagew-signw)*int(x)/100)+int(signw)] = imdoc_portion
	imdoc = cv2.cvtColor(imdoc,cv2.COLOR_BGR2RGB)
	blended_img = Image.fromarray(imdoc)
	pages[i] = blended_img
	
	showImg(i)
	#cv2.waitKey(0)


def placeSign():
	global showSign
	if(len(pages)==0):
		messagebox.showerror("Document not found","Please select the PDF file to insert the signature!!")
		openFile()
		return
	photo = sign.resize((sgw,sgh))
	signImg = ImageTk.PhotoImage(photo)
	showSign.place(relx = (1-float(pgw)/sw)/2+ float(x)*((pgw-sgw)/(sw*100)) ,rely =float(y)*((pgh-sgh)/(page_height*100)) ,relwidth = 0.15*(1+zoom), relheight = 0.15*(1+zoom))
	print(pgh)
	print(page_height)
	showSign.configure(image = signImg)
	showSign.update(image = signImg)
	#mainloop()

def openSign():
	file = askopenfile(mode = 'r' ,initialdir = "/", filetypes =[('Image files',('*.jpg','*.jpeg','*.png'))])
	if file is not None:
		signPath = file.name
		global sign
		sign_check_img =  cv2.imread(signPath)
		sign_check_img.resize(200,int(sign_check_img.shape[1]/sign_check_img.shape[0]*200),3)
		brightPixels = 0
		totPixels = 0
		darkPixels = 0
		for i in range(sign_check_img.shape[0]):
			for j in range(sign_check_img.shape[1]):
				if(sign_check_img[i][j][0]>200 and sign_check_img[i][j][1]>200 and sign_check_img[i][j][2]>200):
					brightPixels = brightPixels+1
				totPixels = totPixels+1
				if(sign_check_img[i][j][0]<100 or sign_check_img[i][j][1]<100 or sign_check_img[i][j][2]<100):
					darkPixels = darkPixels+1
		
		if( float(darkPixels)/totPixels > 0.1 and float(brightPixels)/totPixels < 0.7):
			messagebox.showinfo("Upload a proper Signature", "The signature you have uploaded doesn't seem to be signature. Please upload a clear Image")
			openSign()
			return
		img = open(signPath,"rb")
		sign = Image.open(img)
		photo = sign.resize((int(0.15*sw),int(0.15*sh)))
		signImg = ImageTk.PhotoImage(photo)
		siglabel.configure(image = signImg)
		messagebox.showinfo("Next Step", "Set the zoom value first and then proceed to set x and y coordinates of signature to be inserted!!")
		# siglabel.update(image = signImg)
		mainloop()

def getZoom(z):
	global zoom
	zoom = float(str(z))/100
	global sgw
	global sgh
	sgw = int(0.15*sw*(1+zoom))
	sgh = int(0.15*sh*(1+zoom))
	placeSign()

def getX(a):
	global x
	x = a
	placeSign()

def getY(b):
	global y
	y = b
	placeSign()

def openFile():
	file = askopenfile(mode = 'r',initialdir = "/" , filetypes =[('Pdf Files','*.pdf')])
	if file is not None:
		global path
		path = file.name
		global pages
		pages = convert_from_path(path)
		global num
		num = len(pages)
		showImg(0)
		
def showImg(i):
	global num
	global pages
	if(i<num and i>=0):
		global pdflabel
		pdflabel.pack_forget()
		global pageNo
		pageNo.pack_forget()	
		global pgh
		global pgw
		pgh = page_height
		pgw = pages[i].width * page_height / pages[i].height
		if(pgw/sw>0.5):
			pgw = 0.5*sw
			pgh = pages[i].height * pgw/pages[i].width
		img = ImageOps.fit(pages[i], (int(pgw), int(pgh)))
		photo = ImageTk.PhotoImage(img)
		pdflabel.configure(image = photo)
		pdflabel.place(relx = (1-float(pgw)/sw)/2, rely = 0.00, relwidth = float(pgw)/sw, relheight = pgh/page_height)
		pageNo.configure(text=str(i+1)+"/"+str(num),bg = "#9AFF9A",fg = '#8B475D')
		mainloop()


pdfButton = PhotoImage(file = "open_pdf.png")
signButton = PhotoImage(file = "open sign.png")
attachButton = PhotoImage(file = "sign.png")
saveButton = PhotoImage(file = "save.png")
prevButton = PhotoImage(file = "prev.png")
nextButton = PhotoImage(file = "next.png")
BackgroundImg = PhotoImage(file = "bg-01.png")


tk.Label(window,bg = "#C1FFC1").place(relx = 0,rely = 0,relheight=1,relwidth=1)
tk.Button(window,image = pdfButton,bg="#C1FFC1" ,text = "Open PDF", command = lambda:openFile()).place(relx = 0.05, rely = 0.05)
tk.Button(window,image =signButton,bg="#C1FFC1", text = "Open Signature", fg = 'white',command = lambda:openSign()).place(relx = 0.05, rely = 0.25)
tk.Button(window,image =attachButton,bg="#C1FFC1", text = "Attach Signature",fg = 'white', command = lambda:call_blend()).place(relx = 0.05, rely = 0.45)
tk.Button(window,image =saveButton,bg="#C1FFC1", text = "Save", fg = 'white', command = lambda:savePdf()).place(relx = 0.05, rely = 0.65)

tk.Button(window,image =nextButton,bg="#C1FFC1",text = "Next", fg = "white" , command = lambda:nextPage()).place(relx = 0.8 , rely = 0.9)
tk.Button(window,image =prevButton,bg="#C1FFC1",text = "Prev", fg = "white" , command = lambda:prevPage()).place(relx = 0.12 , rely = 0.9)

xslider = tk.Scale(window, from_=0, to=100,bg="#EEE685", command =getX)
xslider.place(relx = 0.83, rely = 0.65, relwidth = 0.05, relheight = 0.15 )
yslider = tk.Scale(window, from_=0, to=100,bg="#EEE685", command = getY)
yslider.place(relx = 0.9, rely = 0.65, relwidth = 0.05, relheight = 0.15)
zoom = tk.Scale(window,from_=-50, to=100,showvalue=50, orient="horizontal",bg="#EEE685" ,command = getZoom)
zoom.place(relx = 0.8, rely = 0.5, relwidth = 0.15, relheight = 0.05)

tk.Label(window, text = ' X-position',bg="#EEE685").place(relx = 0.83, rely = 0.6, relwidth = 0.05, relheight = 0.05)
tk.Label(window, text = ' Y-position',bg="#EEE685").place(relx = 0.9, rely = 0.6, relwidth = 0.05, relheight = 0.05)
tk.Label(window, text = ' Zoom',bg="#C1FFC1").place(relx = 0.85, rely = 0.45, relwidth = 0.05, relheight = 0.05)


pdflabel = tk.Label(window, text = 'PDF Preview',bg='black',fg='white')
siglabel = tk.Label(window, text = ' Signature Preview',font = "BOLD", bg='#548B54',fg='white')
siglabel.place(relx = 0.8, rely = 0.15, relwidth = 0.15, relheight = 0.15 )
tk.Label(window, text = 'Page No.',bg="#9AFF9A",fg = "#551A8B",font = "BOLD").place(relx = 0.76, rely = 0.74, relwidth = 0.05, relheight = 0.03)
pageNo = Label(window,bg = "#9AFF9A")
pageNo.place(relx = 0.76 , rely = 0.77,relwidth = 0.05, relheight = 0.04)
showSign = tk.Label(window)

window.mainloop()
