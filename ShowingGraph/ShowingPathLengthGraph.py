import pandas as pd
import matplotlib.pyplot as plt
import pathlib

date = "23-08-01 19-24-19"
date = "23-08-07 19-14-18"
mode = "train"
mode = "val"

df = pd.read_csv("log/" + date + "/" + mode + "/metrics.csv", names=['time', 'picture', 'ci', 'episode_length', 'exp_area', 'path_length'], header=None)
plt.plot(df['time'], df['path_length'], color="blue", label="Unlearned Environment")

date = "23-08-07 20-15-58"
df2 = pd.read_csv("log/" + date + "/" + mode + "/metrics.csv", names=['time', 'picture', 'ci', 'episode_length', 'exp_area', 'path_length'], header=None)
plt.plot(df2['time'], df2['path_length'], color="red", label="Learned Environment")

#ラベルの追加
plt.xlabel('Training Steps')
plt.ylabel('Path Length')

#表示範囲の指定
plt.xlim(0, 25000000)
#plt.ylim(0, 1.0)

#凡例の追加
plt.legend()

#指数表記から普通の表記に変換
plt.ticklabel_format(style='plain',axis='x')
plt.ticklabel_format(style='plain',axis='y')

#フォルダがない場合は、作成
p_dir = pathlib.Path("./result/" + mode + "/path_length_graph")
if not p_dir.exists():
    p_dir.mkdir(parents=True)

#グラフの保存
plt.savefig('./result/' + mode + '/path_length_graph/' + date + '.png')

#グラフの表示
plt.show()

print("Showing Path Length graph is completed.")