#Note: everything in here is grouped according to hared function.
# That means that everything to do with import files will be up top,
# all data manipulations for generating the training data is grouped
# together, etc.

#All the imports.
import gensim
import codecs
from gensim import corpora, models, similarities
import nltk
import csv
import pandas as pd
import tempfile
import codecs
import csv
import tensorflow as tf

#In order to build a tag-embedding layer for EVERYTHING.
readfile = input('Where are your fucking morphemes and tags, fuckface???  ')
readinto_COLUMNS = ['word', 'tags']
df_readinto = pd.read_csv(readfile, names=readinto_COLUMNS, skipinitialspace=True)
NCLASSES = len(df_readinto['tags']) + 1
print(NCLASSES)

#variables
Word2Vecmodel = input('Where are your word embeddings coming from, shitbags? ')
training_data_location = input('Where is your training data going, goat-gargler?? ')

model = models.Word2Vec.load(Word2Vecmodel)
word = model.wv.vocab

#Just some notes when the program is run/
print('Make sure to (1) run build_DNNarray(\'the lexeme you\'re interested in\'), and then (2) run_rabbit_run()')

#Pulls data from the corpus and formats it
def build_DNNarray(WORD=word, MODEL=model):
    array = []
    label_values = list(df_readinto['tags'].values)
    vec_values = list(df_readinto['word'].values)
    with codecs.open(training_data_location, 'a', 'utf-8') as csvfile:
        databuilder = csv.writer(csvfile, delimiter=',',
                                 quotechar='',
                                 quoting=csv.QUOTE_MINIMAL)
        for item in label_values:
                array.append(list(model[vec_values[label_values.index(item)]]))
                array.append(label_values.index(item))
                databuilder.writerow(array)
                array=[]
    csvfile.close()


#Components for the DNN. Since we're playing with vectors,
#I ended up de-activating sections relating to categorical columns--they weren't necessary.
COLUMNS = list(range(100)) + ['tag1']
LABEL_COLUMN = inty = tf.contrib.layers.sparse_column_with_hash_bucket('tag1', hash_bucket_size=int(1000), dtype=tf.string)
CONTINUOUS_COLUMNS = list(range(100))

def input_fn(df):
  # Creates a dictionary mapping from each continuous feature column name (k) to
  # the values of that column stored in a constant Tensor.
  continuous_cols = {k: tf.constant(df[k].values)
                     for k in CONTINUOUS_COLUMNS}
  # Creates a dictionary mapping from each categorical feature column name (k)
  # to the values of that column stored in a tf.SparseTensor.
  categorical_cols = {k: tf.SparseTensor(
      indices=[[i, 0] for i in range(df[k].size)],
      values=df[k].values,
      dense_shape=[df[k].size, 1])
                      for k in CATEGORICAL_COLUMNS}
  # Merges the two dictionaries into one.
  feature_cols = dict(continuous_cols.items())
  # Converts the label column into a constant Tensor.
  label = tf.constant(df[LABEL_COLUMN].values)
  # Returns the feature columns and the label.
  return feature_cols, label

def train_input_fn():
  return input_fn(df_train)

def eval_input_fn():
  return input_fn(df_test)

model_dir = tempfile.mkdtemp()

features = []

#transforms the inputs into real_value_columns that TF can manipulate.
def make_features(columns=CONTINUOUS_COLUMNS):
    for k in CONTINUOUS_COLUMNS:
        for item in list(range(len(CONTINUOUS_COLUMNS))):
            item = tf.contrib.layers.real_valued_column(k)
            features.append(item)

#The following two lists are place-holders prior to running actual model in run_rabbit_run()
wide_columns=[0]
deep_columns=[]

#The actual model.
m = tf.contrib.learn.DNNLinearCombinedClassifier(
    model_dir=model_dir,
    linear_feature_columns=wide_columns,
    dnn_feature_columns=deep_columns,
    dnn_hidden_units=[100],
    n_classes=NCLASSES)

#run this to put everything together after you've built some training data.
def run_rabbit_run():
    make_features()
    wide_columns = features
    deep_columns = []
    df_train = pd.read_csv(training_data_location, names=COLUMNS, skipinitialspace=True)
    #df_test = pd.read_csv('/Users/ZaqRosen/Desktop/ARAPAHO_test_data.csv', names=COLUMNS, skipinitialspace=True, skiprows=1))
    wide_collumns = make_features()
    m.fit(input_fn=train_input_fn, steps=2000)
    #results = m.evaluate(input_fn=eval_input_fn, steps=20)
    #print(results)
    var = tf.trainable_variables()
    print(var)