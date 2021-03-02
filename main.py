import NetEase
import requests
from datetime import datetime
from moviepy.editor import *
from adjust import Adjust

now_date = datetime.today()
DateString = now_date.strftime("%Y-%m-%d %I.%M.%S")

# 运行前需要输入的全局变量
SourceMp3Name = input("输入mp3全名:")
KeyWord = ".".join(SourceMp3Name.split(".")[:-1])


def DownloadMV(MVID, filename):
    MVAPI = f"https://api.imjad.cn/cloudmusic/?type=mv&id={MVID}"

    for i in ["1080", "720", "480", "360"]:
        try:
            url = requests.get(MVAPI).json()['data']['brs'][i]
            print(f"【开始下载{i}P MV...】")
            req = requests.get(url, headers=MyHeader)
            filesize = int(req.headers['content-length']) / (1024 ** 2)

            with open(filename, "wb") as MVFile:
                MVFile.write(req.content)
            print(f"【{filename} ({filesize:.2f}MB) 已保存！】")
            break
        except KeyError:
            continue


# 一般MV都有自带字幕的，所以就不用另外做字幕ass文件了
def DownloadLrc():
    pass


MyHeader = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 Edg/81.0.416.72"}

MVID = NetEase.Search(KeyWord, "mvs", limit=1)[0][0]

# 创建工作目录
WorkingDir = f"{KeyWord} {DateString}"
os.makedirs(WorkingDir)

# 下载MV
MVFilePath = f".\{WorkingDir}\{KeyWord}.mp4"
DownloadMV(MVID, MVFilePath)

# 将MV和源MP3混流
SrcVideo = VideoFileClip(MVFilePath)
SrcAudio1 = SrcVideo.audio
Audio1FilePath = f".\\{WorkingDir}\\TempAudio1.mp3"
Audio2FilePath = f".\\{WorkingDir}\\TempAudio2.mp3"
print("【正在分离MV音频...】")
SrcAudio1.write_audiofile(Audio1FilePath)

# 对齐音轨
Adjust(Audio1FilePath, SourceMp3Name, Audio2FilePath)

DstVideo = SrcVideo.set_audio(AudioFileClip(Audio2FilePath))
DstVideo.write_videofile(f"{KeyWord}.mp4")
