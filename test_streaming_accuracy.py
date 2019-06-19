import os
import logging
import soundfile as sf
import tensorflow as tf
import numpy as np
from recognize_command import RecognizeCommands, RecognizeResult
from streaming_accuracy_utils import StreamingAccuracyStats
from figure_utils import *
import time
import wave
import matplotlib.pyplot as plt
# Reads a model graph definition from disk, and creates a default graph object

def load_graph(mode_file):
    graph = tf.Graph()
    with graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(mode_file, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
    return graph


# Takes a file name, and loads a list of labels from it, one per line, and
# returns a vector of strings.

def read_label_file(file_name):
    label_list = []
    with open(file_name, 'r') as f:
        lines = f.readlines()
        for line in lines:
            label_list.append(line.strip())
    return label_list

# Takes a file name, loads a piece of wav from it, and return sample_rate and numpy data of np.float64

def read_wav_file(file_name):
    data, sample_rate = sf.read(file_name, dtype='float32')
    return sample_rate, data



def main():
    wav_file = r"C:\Users\Administrator\Desktop\Mankin2\D8albsounds光肩星天牛.wav"
    logging.basicConfig(level=logging.INFO)

    ground_truth_file = r'E:\1.txt'

    label_file = r"E:\tmp\speech_commands_train\conv_labels.txt"
    model_file = r'E:\1frozen_graph.pb'

    #  ops = tf.get_default_graph().get_operations()
    #  all_tensor_names = {output.name for op in ops for output in op.outputs}
    input_data_name = "decoded_sample_data:0"
    input_rate_name = "decoded_sample_data:1"
    output_softmax_label_name = 'labels_softmax:0'

    clip_duration_ms = 300
    clip_stride_ms = 10

    average_window_duration_ms = 200
    detection_threshold = 0.3
    suppression_ms = 600
    time_tolerance_ms = 100
    verbose = True

    label_list = read_label_file(label_file)
    sample_rate, data = read_wav_file(wav_file)
    channel_count = 1

    cur_time = time.time()

    recognize_commands = RecognizeCommands(labels=label_list,
                                           average_window_duration_ms=average_window_duration_ms,
                                           detection_threshold=detection_threshold,
                                           suppression_ms=suppression_ms,
                                           minimum_count=4)

    stats = StreamingAccuracyStats()
    stats.read_ground_truth_file(ground_truth_file)
    recognize_element = RecognizeResult()
    all_found_words = []


    sample_count = data.shape[0]
    clip_duration_samples = int(clip_duration_ms * sample_rate / 1000)
    clip_stride_samples = int(clip_stride_ms * sample_rate / 1000)
    audio_data_end = sample_count - clip_duration_samples

    # load model and create a tf session to process audio pieces
    log_file_path = r'E:\result2.txt'
    recognize_graph = load_graph(model_file)

    #if exists, clear log path contents
    if os.path.exists(log_file_path):
        os.remove(log_file_path)
    with recognize_graph.as_default():
        with tf.Session() as sess:
            # Get input and output tensor
            audio_data_tensor = tf.get_default_graph().get_tensor_by_name(input_data_name)
            audio_sample_rate_tensor = tf.get_default_graph().get_tensor_by_name(input_rate_name)
            output_softmax_label_tensor = tf.get_default_graph().get_tensor_by_name(output_softmax_label_name)

            for audio_data_offset in range(0, audio_data_end, clip_stride_samples):
                input_start = audio_data_offset
                input_end = audio_data_offset + clip_duration_samples
                outputs = sess.run(output_softmax_label_tensor,
                                   feed_dict={audio_data_tensor: np.expand_dims(data[input_start:input_end], axis=-1),
                                              audio_sample_rate_tensor: sample_rate})

                outputs = np.squeeze(outputs)
                current_time_ms = int(audio_data_offset * 1000 / sample_rate)
                try:
                    recognize_commands.process_latest_result(outputs, current_time_ms, recognize_element)
                except Exception as e:
                    logging.error("Recognition processing failed: " + str(e))
                    return

                #if recognize_element.is_new_command and recognize_element.found_command != '_silence_':
                if recognize_element.is_new_command:
                    all_found_words.append([recognize_element.found_command, current_time_ms])

                    if verbose:
                        stats.calculate_accuracy_stats(all_found_words, current_time_ms, time_tolerance_ms)
                        try:
                            recognition_state = stats.delta()
                        except Exception as e:
                            logging.error("Statistics delta computing failed: " + str(e))
                        else:
                            logging.info(str(current_time_ms) + "ms: " + recognize_element.found_command + ": " +
                                         str(recognize_element.score) + recognition_state)

                            f = open(log_file_path, 'a')
                            write_str = str(current_time_ms) + ':' + recognize_element.found_command + '\n'
                            f.write(write_str)
                            f.close()
                            stats.print_accuracy_stats()

    stats.calculate_accuracy_stats(all_found_words, -1, time_tolerance_ms)
    stats.print_accuracy_stats()

    #show the recognized field in different colors
    #show_recognized(wav_file, log_file_path)


if __name__ == "__main__":
    main()

