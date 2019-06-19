import wave
import numpy as np
import matplotlib.pyplot as plt


def show_recognized(wav_file, result_file):

    plt.title('Start point in wav file')

    #时域波形
    file = wave.open(wav_file, 'rb')
    params = file.getparams()
    framerate, nframes = params[2], params[3]
    str_data = file.readframes(nframes)
    file.close()

    tianniu_mark_time = []
    chouchun_mark_time = []
    noise_mark_time = []
    silence_mark_time = []

    # 从result文件读取时间点并添加标注
    with open(result_file) as f:
        data = f.readlines()
        for line in data:
            prev_label = 'silence'
            cur_mark_time = int(line.split(':')[0]) / 1000
            cur_label = line.split(":")[-1][0:-1]#log文件最后有换行符
            o = int(cur_mark_time * framerate)
            if cur_label == "tianniu" and cur_label != prev_label:
                tianniu_mark_time.append(o)
                prev_label = cur_label
            elif cur_label == 'chouchun' and cur_label != prev_label:
                chouchun_mark_time.append(o)
                prev_label = cur_label
            elif cur_label == 'noise'  and cur_label != prev_label:
                noise_mark_time.append(o)
                prev_label = cur_label
            elif cur_label == '_silence_'  and cur_label != prev_label:
                silence_mark_time.append(o)
                prev_label = cur_label


    wav_data = np.fromstring(str_data, dtype=np.short)
    time = np.arange(0, nframes) * (1.0 / framerate)
    tianniu_mark_x, tianniu_mark_y = [], []
    chouchun_mark_x, chouchun_mark_y = [], []
    noise_mark_x, noise_mark_y = [], []
    silence_mark_x, silence_mark_y = [], []
    for i in tianniu_mark_time:
        tianniu_mark_x.append(time[i])
        tianniu_mark_y.append(0)
    for i in chouchun_mark_time:
        chouchun_mark_x.append(time[i])
        chouchun_mark_y.append(0)
    for i in noise_mark_time:
        noise_mark_x.append(time[i])
        noise_mark_y.append(0)
    for i in silence_mark_time:
        silence_mark_x.append(time[i])
        silence_mark_y.append(0)

    plt.xlabel('time')
    plt.ylabel('Volume')
    mainp, =plt.plot(time, wav_data, '-', c='black')
    p1, =plt.plot(tianniu_mark_x, tianniu_mark_y, 'o', c='red')
    p2, =plt.plot(chouchun_mark_x, chouchun_mark_y, 'o', c='blue')
    p3, =plt.plot(noise_mark_x, noise_mark_y, 'o', c='yellow')
    p4, =plt.plot(silence_mark_x, silence_mark_y, 'o', c='white')
    plt.legend([p4,p3,p2,p1],['silence','noise','chouchun','tianniu'], loc='best', shadow=True)
    plt.show()

'''
wav_file = r"E:\converted\chouchun\180804_1841.wav"
log_file_path = r'E:\result2.txt'
show_recognized(wav_file, log_file_path)
'''
