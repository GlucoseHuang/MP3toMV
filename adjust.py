def Adjust(a1, a2, a3):
    from pydub import AudioSegment
    from pydub.playback import play
    import tkinter
    from tkinter import ttk
    from sys import exit

    def Start(a1, a2):
        s = eval(StartPoint.get())
        d = eval(Duration.get())
        ms = LR.get() * eval(offset.get())
        audio1 = AudioSegment.from_mp3(a1)[s:s + d]
        if ms > 0:
            audio2 = AudioSegment.silent(duration=ms) + AudioSegment.from_mp3(a2)[s:s + d - ms]
        elif ms <= 0:
            audio2 = AudioSegment.from_mp3(a2)[s - ms:s - ms + d]
        mixed = audio1.overlay(audio2)
        play(mixed)

    def Finish(a2, a3):
        ms = LR.get() * eval(offset.get())

        if ms > 0:
            TempAudio2 = AudioSegment.silent(duration=ms) + AudioSegment.from_mp3(a2)
        elif ms <= 0:
            TempAudio2 = AudioSegment.from_mp3(a2)[-ms:]
        TempAudio2.export(a3, format='mp3')

        root.quit()

    root = tkinter.Tk()
    root.title('音频对齐')
    root.minsize(310, 55)

    frame = ttk.LabelFrame(root, text="操作")
    frame.grid(column=0, row=0, sticky='W')
    LR = tkinter.IntVar()
    LR.set(1)

    tkinter.Button(frame, text='开始', width=6, height=1, command=lambda: Start(a1, a2)).grid(column=0, row=0, sticky='W')

    tkinter.Radiobutton(frame, text='左移', variable=LR, value=-1, command=lambda: LR.set(-1)).grid(column=2, row=0,
                                                                                                  sticky='W')

    tkinter.Radiobutton(frame, text='右移', variable=LR, value=1, command=lambda: LR.set(1)).grid(column=3, row=0,
                                                                                                sticky='W')

    offset = tkinter.Entry(frame, show=None, width=6)
    offset.insert(0, "0")
    offset.grid(column=1, row=0, sticky='W')

    StartPoint = tkinter.Entry(frame, show=None, width=6)
    StartPoint.insert(0, "0")
    StartPoint.grid(column=4, row=0, sticky='W')

    Duration = tkinter.Entry(frame, show=None, width=6)
    Duration.insert(0, "3000")
    Duration.grid(column=5, row=0, sticky='W')

    tkinter.Button(frame, text='完成', width=6, height=1, command=lambda: Finish(a2, a3)). \
        grid(column=6, row=0, sticky='W')

    tkinter.mainloop()
