from flask import Flask, render_template

import pandas as pd
import networkx as nx
import base64
import pylab

from io import BytesIO
from matplotlib.pyplot import figure

app = Flask(__name__)

data = pd.read_csv('static/vyborka.csv')
data = data.iloc[:, 0:3]

data['Участник 1'].value_counts()
data['Участник 2'].value_counts()

data2 = data[['№ страхового события', 'Участник 2']]

data2 = data2.rename(columns={"Участник 2": "Участник 1"})

sample = pd.concat([data[['№ страхового события', 'Участник 1']], data2])

bad_guys = sample['Участник 1'].value_counts()
bad_guys = bad_guys[bad_guys > 1]

bads = bad_guys.index.tolist()

result = data[(data['Участник 1'].isin(bads)) | (data['Участник 2'].isin(bads))]
bads = list(result['Участник 1'].unique()) + list(result['Участник 2'].unique())

# Построение графика связей участников
G = nx.from_pandas_edgelist(result, 'Участник 1', 'Участник 2')
figure(figsize=(12, 12))
nx.draw_shell(G, with_labels=True)

img = BytesIO()
pylab.savefig(img, format='png')
pylab.close()
img.seek(0)
plot_url = base64.b64encode(img.getvalue()).decode('utf8')

# Возможные преступные группировки
bad_groups = nx.cycle_basis(G)

# Вывод рейтинга по ДТП
rating = []

for person in data['Участник 1']:
    rating.append(person)

for person in data['Участник 2']:
    rating.append(person)

result = {i: rating.count(i) for i in rating}
sorted_dictionary = dict(sorted(result.items(), key=lambda x: x[1], reverse=True))


@app.route('/')
def main_page():
    return render_template("home.html")


@app.route('/rating')
def accident_rating():
    return render_template("rating.html", sorted_dictionary=sorted_dictionary)


@app.route('/analysis')
def accident_analysis():
    return render_template("analysis.html", bad_groups=bad_groups, plot_url=plot_url)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
