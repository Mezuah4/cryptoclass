# Laundering in Public: Detecting Money Laundering in the Cryptocurrency Economy

## Abstract
The use of cryptocurrency to launder money into the economy and fund illicit activities is a widely discussed problems. There are various published works which explore the task of identifying illicit blockchain entities, but few of them are transparent in their approaches meaning that reproducibility is low.

The aim of this project was to circumvent the issues seen in previous literature by developing a transparent machine learning pipeline which allows for the flagging of suspicious addresses on historical and current data.

A previous successful attempt at classifying Ethereum accounts as licit/illicit was replicated (with various improvements) and then a transparent pipeline was developed for its application to the Bitcoin blockchain. Whilst the replication of the Ethereum approach improved upon the original implementation's accuracy by 1.9\%, the Bitcoin address model exhibited limited success at 73.7\% accuracy.

The differences between the datasets used in the paper were compared statistically based on the strength of the feature-target associations within each dataset. This revealed that the Ethereum dataset contained more strongly associated feature-target pairs than the Bitcoin data extracted - which was likely the cause of the drop in accuracy. Similar issues were also identified in other related works.

The Bitcoin address model was used to estimate the prevalence of suspicious Bitcoin addresses in each month of 2022 and yielded a 31.4\% increase between the first and last months.

## Datasets

Elliptic Dataset: [Here](https://www.kaggle.com/datasets/ellipticco/elliptic-data-set)

Ethereum Dataset: [Here](https://www.sciencedirect.com/science/article/pii/S0957417420301433?casa_token=v8bRcQ5FGgcAAAAA:9Vrqj6e3da_gA6O9HTVW-K7QPBGCus80GPxh7xpAqpP_BbRxMJ-_75wN9zcNBQQw9gTwaBjFaT2s) 

Bitcoin Multiclass: [Here](https://github.com/pranavn91/blockchain)

Bitcoin Single Class: Extracted as Part of this Project

## Summary
Numerous Random Forest models were trained on readily available datasets and model accuracy was compared to that of the model created on my own dataset.

Improvements upon original models were observed but success on my own dataset was limited likely due to low feature/target association strength.

![image](https://github.com/Mezuah4/cryptoclass/assets/43442819/a86fa21a-e1f2-4eeb-a531-6aa0f719bf52)

The resulting model was used to predict the prevalence of suspicious bitcoin addresses in the year 2022.

![image](https://github.com/Mezuah4/cryptoclass/assets/43442819/a3d78669-8cba-46e1-99e4-a94b61e05e6b)
