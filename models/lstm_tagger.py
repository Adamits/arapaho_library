from dynet import *
from collections import Counter
import random

train_file=""
test_file=""

MLP=True

def read(fname):
    sent = []
    for line in file(fname):
        line = line.strip().split()
        if not line:
            if sent: yield sent
            sent = []
        else:
            w,p = line
            sent.append((w,p))

train=list(read(train_file))
test=list(read(test_file))
words=[]
tags=[]
wc=Counter()
for s in train:
    for w,p in s:
        words.append(w)
        tags.append(p)
        wc[w]+=1
words.append("_UNK_")
#words=[w if wc[w] > 1 else "_UNK_" for w in words]
tags.append("_START_")

for s in test:
    for w,p in s:
        words.append(w)

vw = util.Vocab.from_corpus([words])
vt = util.Vocab.from_corpus([tags])
UNK = vw.w2i["_UNK_"]

# size of word matrix, and size of tag matrix
nwords = vw.size()
ntags  = vt.size()

model = Model()
sgd = SimpleSGDTrainer(model)

# For lookup on embeddings
E = model.add_lookup_parameters((nwords, 128))
p_t1  = model.add_lookup_parameters((ntags, 30))

if MLP:
    pH = model.add_parameters((32, 50*2))
    pO = model.add_parameters((ntags, 32))
else:
    pO = model.add_parameters((ntags, 50*2))

builders=[
        LSTMBuilder(1, 128, 50, model),
        LSTMBuilder(1, 128, 50, model),
        ]

def build_tagging_graph(words, tags, builders):
    renew_cg()
    f_init, b_init = [b.initial_state() for b in builders]

    wembs = [E[w] for w in words]
    wembs = [noise(we,0.1) for we in wembs]

    fw = [x.output() for x in f_init.add_inputs(wembs)]
    bw = [x.output() for x in b_init.add_inputs(reversed(wembs))]

    if MLP:
        H = parameter(pH)
        O = parameter(pO)
    else:
        O = parameter(pO)
    errs = []
    for f,b,t in zip(fw, reversed(bw), tags):
        f_b = concatenate([f,b])
        if MLP:
            r_t = O*(tanh(H * f_b))
        else:
            r_t = O * f_b
        err = pickneglogsoftmax(r_t, t)
        errs.append(err)
    return esum(errs)

def tag_sent(sent, builders):
    renew_cg()
    f_init, b_init = [b.initial_state() for b in builders]
    wembs = [E[vw.w2i.get(w, UNK)] for w,t in sent]

    fw = [x.output() for x in f_init.add_inputs(wembs)]
    bw = [x.output() for x in b_init.add_inputs(reversed(wembs))]

    if MLP:
        H = parameter(pH)
        O = parameter(pO)
    else:
        O = parameter(pO)
    tags=[]
    for f,b,(w,t) in zip(fw,reversed(bw),sent):
        if MLP:
            r_t = O*(tanh(H * concatenate([f,b])))
        else:
            r_t = O*concatenate([f,b])
        out = softmax(r_t)
        chosen = np.argmax(out.npvalue())
        tags.append(vt.i2w[chosen])
    return tags


tagged = loss = 0
for ITER in range(50):
    random.shuffle(train)
    for i,s in enumerate(train,1):
        if i % 5000 == 0:
            sgd.status()
            print(loss / tagged)
            loss = 0
            tagged = 0
        if i % 10000 == 0:
            good = bad = 0.0
            for sent in test:
                tags = tag_sent(sent, builders)
                golds = [t for w,t in sent]
                for go,gu in zip(golds,tags):
                    if go == gu: good +=1
                    else: bad+=1
            print(good/(good+bad))
        ws = [vw.w2i.get(w, UNK) for w,p in s]
        ps = [vt.w2i[p] for w,p in s]
        sum_errs = build_tagging_graph(ws,ps,builders)
        squared = -sum_errs# * sum_errs
        loss += sum_errs.scalar_value()
        tagged += len(ps)
        sum_errs.backward()
        sgd.update()