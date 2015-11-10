import Quandl as q
import pandas as pd


def chart(data, series, x, y, title):

	fig = plt.figure(figsize=(12, 12))

	ax = fig.add_subplot(1, 1, 1)

	ax.spines['right'].set_color('none')
	ax.spines['top'].set_color('none')

	ax.set_ylim([min(data[series[0]])-10, max(series[0])+10])

	ax.xaxis.set_ticks_position('bottom')

	plt.title(title)
	plt.xlabel(x)
	plt.ylabel(y)

	# plt.annotate(
	#     'THE DAY I REALIZED\nI COULD COOK BACON\nWHENEVER I WANTED',
	#     xy=(70, 1), arrowprops=dict(arrowstyle='->'), xytext=(15, -10))

	for s in series:
		ax.plot(data.index, data[s], color="b")
		ax.plot(data.index, data[s], color="c")
		ax.plot(data.index, data[s], color="r")

	
	return plt 