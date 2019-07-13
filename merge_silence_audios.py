from pydub import AudioSegment
import os

working_dir = r'E:\Mankin_mono\_background_noise_'
output_dir = r'E:\Mankin_mono_noise'
if os.path.exists(output_dir) is not True:
    os.mkdir(output_dir)
files = os.listdir(working_dir)

remove = []
for file in files:
    if file not in remove:
        prefix = file.split('-')[0]
        file_path = os.path.join(working_dir, file)
        seg = AudioSegment.from_wav(file_path)
        print('prefix:' + prefix)
        remove.append(file)
        for m_file in files:
            print("m_file:" + m_file)
            if m_file.split('-')[0] == prefix:
                new_seg = AudioSegment.from_wav(os.path.join(working_dir, m_file))
                seg = seg + new_seg
                remove.append(m_file)
    seg.export(os.path.join(output_dir, prefix + '.wav'), format='wav')

