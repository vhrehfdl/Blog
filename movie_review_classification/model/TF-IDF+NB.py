from sklearn import preprocessing, naive_bayes, metrics
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import pandas
import csv
from sklearn.metrics import classification_report



def Load_Data(train_file_dir, validation_file_dir):
    train_file = open(train_file_dir, 'r', encoding='utf-8')  # 학습 데이터 파일 읽기
    csv_reader_train = csv.reader(train_file)

    valid_file = open(validation_file_dir, 'r', encoding='utf-8')  # 검증 데이터 파일 읽기
    csv_reader_valid = csv.reader(valid_file)

    all_texts = []
    train_texts, train_labels = [], []
    valid_texts, valid_labels = [], []

    for row in csv_reader_train:
        all_texts.append(row[0])
        train_texts.append(row[0])
        train_labels.append(row[1])

    train_file.close()

    for row in csv_reader_valid:
        all_texts.append(row[0])
        valid_texts.append(row[0])
        valid_labels.append(row[1])

    valid_file.close()

    # 전체, 학습, 검증 데이터 프레임 미리 만들어둔다.
    dfAll, dfTrain, dfValid = pandas.DataFrame(), pandas.DataFrame(), pandas.DataFrame()
    dfAll['text'] = all_texts
    dfTrain['text'], dfTrain['label'] = train_texts, train_labels
    dfValid['text'], dfValid['label'] = valid_texts, valid_labels

    # 라벨링 진행.
    encoder = preprocessing.LabelEncoder()
    train_y, valid_y = encoder.fit_transform(dfTrain['label']), encoder.fit_transform(dfValid['label'])

    DataSet = {'train_text': dfTrain['text'], 'valid_text': dfValid['text'], 'train_label': train_y, 'valid_label': valid_y, 'all_text_data': dfAll['text']}

    return DataSet



def Convert_Text_To_Vector(DataSet, vector_mode):

    AllTextData = DataSet['all_text_data']
    train_text = DataSet['train_text']
    valid_text = DataSet['valid_text']

    word_index, embedding_matrix = None, None  # Word Embedding 일 경우에만 사용한다.

    if vector_mode == "BOW":
        # BOW
        count_vect = CountVectorizer(analyzer='word', token_pattern=r'\w{1,}')
        count_vect.fit(AllTextData)
        train_count = count_vect.transform(train_text)
        valid_count = count_vect.transform(valid_text)

    elif vector_mode == "TF_IDF_COUNT":
        # TF-IDF : 단어 단위로 자른 TF-IDF
        tfidf_vect = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}')
        tfidf_vect.fit(AllTextData)
        train_count = tfidf_vect.transform(train_text)
        valid_count = tfidf_vect.transform(valid_text)

    elif vector_mode == "TF_IDF_NGRAM":
        # TF-TF_IDF_NGRAM : 단어 단위로 자른 TF-IDF에서 N-gram 추가
        tfidf_vect_ngram = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}', ngram_range=(2, 3))
        tfidf_vect_ngram.fit(AllTextData)
        train_count = tfidf_vect_ngram.transform(train_text)
        valid_count = tfidf_vect_ngram.transform(valid_text)

    elif vector_mode == "TF_IDF_CHAR_NGRAM":
        # TF-TF_IDF_CHAR_NGRAM : char(문자) 단위로 자른 TF-IDF에서 N-gram 추가
        tfidf_vect_ngram_chars = TfidfVectorizer(analyzer='char', token_pattern=r'\w{1,}', ngram_range=(2, 3))
        tfidf_vect_ngram_chars.fit(AllTextData)
        train_count = tfidf_vect_ngram_chars.transform(train_text)
        valid_count = tfidf_vect_ngram_chars.transform(valid_text)

    print(train_count.shape)
    print(valid_count.shape)

    TextToVec_DataSet = {'train_count': train_count, 'valid_count': valid_count, 'word_index': word_index, 'embedding_matrix': embedding_matrix}

    return TextToVec_DataSet



def Train_Model(classifier, data_set, text_to_vector_data_set, target_names=['0', '1']):

    train_count, train_label = text_to_vector_data_set['train_count'], data_set['train_label']
    valid_count, valid_label = text_to_vector_data_set['valid_count'], data_set['valid_label']

    # train_count와 train_label로 학습해서 모델 생성.
    classifier.fit(train_count, train_label)

    # 학습된 모델에 valid_count를 넣어 정답 예측하기.
    predictions = classifier.predict(valid_count)

    print("-" * 33)
    print(classification_report(valid_label, predictions, target_names=target_names))

    return metrics.accuracy_score(predictions, valid_label)



if __name__ == "__main__":
    DataSet = Load_Data("../data/train.csv", "../data/validation.csv")          # 1. 학습데이터와 검증데이터를 불러온다.

    TextToVec_DataSet = Convert_Text_To_Vector(DataSet, "TF_IDF_COUNT")         # 2. 불러온 Text 데이터를 Vector로 변환해준다.
    classifier = naive_bayes.MultinomialNB()                                    # 3. 사용할 알고리즘 정의
    accuracy = Train_Model(classifier, DataSet, TextToVec_DataSet)              # 4. model을 만들고 정확도를 측정한다.

    print("TF_IDF_COUNT 모델 정확도: ", accuracy)
    print("-" * 33)



    TextToVec_DataSet = Convert_Text_To_Vector(DataSet, "TF_IDF_NGRAM")
    classifier = naive_bayes.MultinomialNB()
    accuracy = Train_Model(classifier, DataSet, TextToVec_DataSet)

    print("TF_IDF_NGRAM 모델 정확도: ", accuracy)
    print("-" * 33)



    TextToVec_DataSet = Convert_Text_To_Vector(DataSet, "TF_IDF_CHAR_NGRAM")
    classifier = naive_bayes.MultinomialNB()
    accuracy = Train_Model(classifier, DataSet, TextToVec_DataSet)

    print("TF_IDF_CHAR_NGRAM 모델 정확도: ", accuracy)
    print("-" * 33)

