from nexuralnetweb import celery
import nexuralnet

@celery.task()
def trainNetworkTask(networkArhitecturePath, trainingFilePath, dataPath, labelsPath, outputTrainedDataFilePath, outputTrainerInfoFolderPath, trainingDataSource, targetDataSource):
	try:
		print '[INFO] Starting a new training:'
		if trainingDataSource == "MNIST_DATA_FILE":
			internalTrainingDataSource = nexuralnet.trainer.trainingDataSource.MNIST_DATA_FILE
			internalTargetDataSource = nexuralnet.trainer.targetDataSource.MNIST_DATA_FILE
		trainer = nexuralnet.trainer(networkArhitecturePath, trainingFilePath)
		print '--- created training network.'
		print '--- started training.'
		trainer.train(dataPath, labelsPath, outputTrainedDataFilePath, outputTrainerInfoFolderPath, internalTrainingDataSource, internalTargetDataSource)
		print '[!] Finished training.'
	except RuntimeError as exc:
		print("[ERROR] " + str(exc))
	except:
		print("[ERROR] Unknown!")


@celery.task()
def trainNetworkTaskFromOtherTraining(networkArhitecturePath, trainingFilePath, weightFilePath, dataPath, labelsPath, outputTrainedDataFilePath, outputTrainerInfoFolderPath, trainingDataSource, targetDataSource):
	try:
		print '[INFO] Starting a new training based on another:'
		if trainingDataSource == "MNIST_DATA_FILE":
			internalTrainingDataSource = nexuralnet.trainer.trainingDataSource.MNIST_DATA_FILE
			internalTargetDataSource = nexuralnet.trainer.targetDataSource.MNIST_DATA_FILE
		trainer = nexuralnet.trainer(networkArhitecturePath, trainingFilePath)
		print '--- created training network.'
		trainer.deserialize(weightFilePath)
		print '--- loaded weights from previous training.'
		print '--- started training.'
		trainer.train(dataPath, labelsPath, outputTrainedDataFilePath, outputTrainerInfoFolderPath, internalTrainingDataSource, internalTargetDataSource)
		print '[!] Finished training.'
	except RuntimeError as exc:
		print("[ERROR] " + str(exc))
	except:
		print("[ERROR] Unknown!")