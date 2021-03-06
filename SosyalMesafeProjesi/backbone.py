# Zaten eğitilmiş bir model mevcut o yüzden onu kullandım.
# https://github.com/tensorflow/models/tree/master/research/object_detection
# bu kodun bir parçası olarak kullanıldı.

import glob, os, tarfile, urllib
import tensorflow as tf
from utils import label_map_util


def set_model(model_name, label_name):
    model_found = 0

    for file in glob.glob("*"):
        if file == model_name:
            model_found = 1

    # Hangi modelin indirileceği.
    model_name = model_name
    model_file = model_name + ".tar.gz"
    download_base = "http://download.tensorflow.org/models/object_detection/"

    # Bu, nesne tespiti için kullanılan gerçek modeldir.
    path_to_ckpt = model_name + "/frozen_inference_graph.pb"

    # Her kutuya doğru etiket eklemek için kullanılan dizelerin listesi.
    path_to_labels = os.path.join("data", label_name)

    num_classes = 90

    # Henüz indirilmemişse Modeli İndir
    if model_found == 0:
        opener = urllib.request.URLopener()
        opener.retrieve(download_base + model_file, model_file)
        tar_file = tarfile.open(model_file)
        for file in tar_file.getmembers():
            file_name = os.path.basename(file.name)
            if "frozen_inference_graph.pb" in file_name:
                tar_file.extract(file, os.getcwd())

    # Belleğe bir (donmuş) Tensorflow modeli yükleyin.
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(path_to_ckpt, "rb") as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name="")

    # Etiket haritasını yükle
    # Etiket, harita indekslerini kategori adlarına eşler, böylece evrişim ağımız
    # 5'i tahmin ettiğinde, bunun uçağa karşılık geldiğini bilir.
    # Burada dahili yardımcı program işlevlerini kullanıyorum, ancak tam sayıları uygun
    # dize etiketlerine eşleyen bir sözlük döndüren herhangi bir şey yeterli olacaktır.

    label_map = label_map_util.load_labelmap(path_to_labels)
    categories = label_map_util.convert_label_map_to_categories(
        label_map, max_num_classes=num_classes, use_display_name=True
    )
    category_index = label_map_util.create_category_index(categories)

    return detection_graph, category_index
