from nexuralnetweb import celery
import nexuralnet

@celery.task()
def trainNetworkTask(networkArhitecturePath, trainingFilePath, dataPath, labelsPath, outputTrainedDataFilePath, outputTrainerInfoFolderPath, trainingDataSource, targetDataSource):
	print 'Started training...'
	if trainingDataSource == "MNIST_DATA_FILE":
		internalTrainingDataSource = nexuralnet.trainer.trainingDataSource.MNIST_DATA_FILE
		internalTargetDataSource = nexuralnet.trainer.targetDataSource.MNIST_DATA_FILE
	trainer = nexuralnet.trainer(networkArhitecturePath, trainingFilePath)
	trainer.train(dataPath, labelsPath, outputTrainedDataFilePath, outputTrainerInfoFolderPath, internalTrainingDataSource, internalTargetDataSource)
	print 'Finished training.'