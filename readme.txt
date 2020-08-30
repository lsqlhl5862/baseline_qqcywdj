
8月30日更新
1、请将test.csv、train.csv放在datasets目录下，否则要花4个小时处理所有PDF
2、验证集某个字段的分数可以参考以下代码:

  def get_F1(val_pred, val_true):
      val_pred = list(val_pred)
      val_true = list(val_true)
      curr = list(set(val_pred).intersection(set(val_true)))
      R = len(curr)/len(val_true)
      P = len(curr)/len(val_pred)
      return 2*P*R/(P+R)

  r = pd.merge(val_df[['sample_id']], train_outputs, on='sample_id', how='left')
  val_true = r['sample_id'].astype(str) + r['认购日期'].astype(str) + r['理财产品名称'].astype(str) + r['理财类型'].astype(str) + r['认购金额(万元)'].astype(str) + r['产品起息日'].astype(str)+ r['产品到息日'].astype(str) + r['产品期限'].astype(str) + r['资金来源'].astype(str) + r['实际购买公司名称'].astype(str) + r['实际购买公司和上市公司关系'].astype(str) + r['买卖方是否有关联关系'].astype(str) + r['公告日期'].astype(str)

  r = val_result
  val_pred = r['sample_id'].astype(str) + r['认购日期'].astype(str) + r['理财产品名称'].astype(str) + r['理财类型'].astype(str) + r['认购金额(万元)'].astype(str) + r['产品起息日'].astype(str)+ r['产品到期日'].astype(str) + r['产品期限'].astype(str) + r['资金来源'].astype(str) + r['实际购买公司名称'].astype(str) + r['实际购买公司和上市公司关系'].astype(str) + r['买卖方是否有关联关系'].astype(str) + r['公告日期'].astype(str)

  score = get_F1(val_pred, val_true)
  score
  
  只需要选择对应的字段ID即可计算
3、results\re_lstm_base.csv 是baseline的运行结果
4、results\true_vs_pred.csv是baseline验证对比的结果
5、目前暂无true_vs_pred.csv，原因是预测和实际行数完全不匹配，大多数的Pdf都有存在多预测的情况，这是首先要解决的问题——————梁洪亮、傅逸雯（切割逻辑）
6、理财产品名称几乎对不上，这是第二要解决的问题———————杨志玮、魏嘉辰（切割逻辑）
7、日期问题为第三要解决的问题，等上述问题处理好再议。
---------------
使用到的库以及版本：
pandas 0.25.3
numpy  1.18.1
pdfplumber 0.5.22(pip install pdfplumber)
tqdm   4.48.0
sklearn  0.21.3
scipy  1.2.1
jieba  0.39(pip install jieba)
tensorflow 1.9.0(pip install tensorflow)
gensim  3.8.1(pip install gensim==3.8.1)
keras  2.2.4(pip install keras)

git branch --set-upstream-to=baseline_qqcywdj/master master
分析赛题和数据格式可以发现需要预测的label有13个字段
数据分为三类数据，分别采用不同方法抽取

认购日期                    多组数据
理财产品名称                 多组数据
产品发行方名称               多组数据
理财类型                    classtype数据（10类）
认购金额(万元)               多组数据
产品起息日                   多组数据
产品到息日                   多组数据
产品期限                     多组数据
资金来源                    classtype数据（3类）
实际购买公司名称             sample整体数据
实际购买公司和上市公司关系   classtype数据（3类）
买卖方是否有关联关系         classtype数据（2类）
公告日期                    sample整体数据

此赛题不能直接用基于spo的方法进行数据抽取，因为很多字段label在打标签的时候进行了规范化
并且每一个sampleid包含多组数据，因此对这部分多组数据需采用正则或者规则等手段进行抽取并进行规范化

基本思路：
1、首先数据是pdf数据因此我们需要先把数据里面的文本或者表格抽取出来，此处采用pdfplumber库进行抽取
2、这里直接对tabel数据进行处理，一个sampleid数据里面包含多组数据，通过分析数据可以得到每个字段抽取的相关规则，首先抽取的是多组数据
  产品起息日-产品到息日-产品期限-认购日期      采用正则匹配的方式抽取时间(这里需要考虑多组类型2019-08-17，2019/8/17， 2019年8月17日等操作)，然后认为前一个时间是起息日，后一个时间是到息日，而产品期限则是这俩个时间相减
  认购金额                                 观察数据会发现金额大多数会包含（，）符号，因此判断除去此符号后是否是数字即可，但是需要特别注意最后结果是万元，有些字段是元因此需要除以10000
  产品发行方名称   这部分直接判断后两个字是什么东西，通过统计训练集会发现末尾俩个字一般是（银行、公司、企业等）
  理财产品名称     前几个数据判断完了，在列表里面剩下的第一列就认为是此类数据
3、然后对sample整体数据
  实际购买公司名称 分析后发现一般在text以/n划分的列表里面的第一个包含有限公司的数据
  公告日期         一般text最后一个日期即是公告日期
4、对classtype数据
  输入：text1 理财产品名称+_+产品发现方名称         text2 pdf中抽取的文本数据
  直接采用双输入到lstm中，然后两个输入的dense层进行交互得到最后结果，这里建模方式是4输出网络
5、最后将抽取出来的数据进行整理即可
