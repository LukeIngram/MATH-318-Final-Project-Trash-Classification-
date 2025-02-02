# knn_pixels.py
# monolithic script to evaluate knn classification with raw pixel data
# NOTE: DO NOT RUN OUTSIDE OF HEAVY COMPUTE ENVIRONMENT

from sklearn.model_selection import train_test_split,cross_val_score
from sklearn.decomposition import IncrementalPCA 
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix,classification_report
import matplotlib.pyplot as plt 
import numpy as np 
import pandas as pd 
from tqdm import tqdm

import cv2
import glob


# K-fold Cross-validated KNN using sklearn. & plots score h
def crossValidate(X,Y,folds=10,kmax = 10):
    kscores = []
    for i in tqdm(range(1,kmax)):
        knn = KNeighborsClassifier(n_neighbors=i,n_jobs=8) # 5 parallel tasks to speed things up
        cv = cross_val_score(knn,X,Y,cv=folds,scoring="accuracy")
        kscores.append(cv.mean())
    
    plt.plot(list(range(1,kmax)),kscores,'bx-')  
    plt.xticks(np.arrange(1,kmax)+1,1.0)
    plt.savefig("Optimal_neighbors_pixel.png")
    plt.show()



def main():
 
    # Load & flatten entire dataset to memory
    imgPaths = glob.glob("../src/data/archive/Garbage_classification/load/*.jpg")
    X_raw = np.array([np.array(cv2.imread(img)) for img in imgPaths])
    X_data = X_raw.flatten().reshape(2527,589824) # flatten & reshape to retain features

    df = pd.read_csv("data/archive/zero-indexed-files.txt",sep=' ')
   
    print(df.head(5)) #DEBUG

    
    X_train,X_test,Y_train,Y_test = train_test_split(np.array([X_data[:,i] for i in range(X_data.shape[1])]).T,df['class'],
                                                     test_size=0.20,random_state=42,stratify=df['class'])
    
    # Reduce down with PCA (using as many components as our RAM limitations allow)
    
    Xs_train = X_train/255.0
    Xs_test = X_test/255.0

    pca = IncrementalPCA(n_components = None,batch_size=10) # incremental used as entire set cannot fit into memory 
    tqdm(pca.fit(Xs_train))
    Xs_train_reduced = pca.transform(Xs_train) 
    Xs_test_reduced = pca.transform(Xs_test)
    
    print(sum(pca.explained_variance_ratio_))

    print(f"Dimensions of data after PCA: {Xs_train_reduced.shape}") 

    # find optimal neighbors
    crossValidate(Xs_train_reduced,Y_train,kmax=50)
    

    #knn = KNeighborsClassifier()

if __name__ == '__main__': 
    main()