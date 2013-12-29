LOCK TABLES `pyscada_globalconfig` WRITE;
/*!40000 ALTER TABLE `pyscada_globalconfig` DISABLE KEYS */;

INSERT INTO `pyscada_globalconfig` (`id`, `key`, `value`, `description`)
VALUES
	(1,'repeatings','0','record data only an specified number of times (1..n) or all the time (0)'),
	(2,'silentMode','1','print messages to the console'),
	(3,'stepsize','5','time between the measurements in seconds'),
	(4,'simulation','1','simulate measurement data  ');

/*!40000 ALTER TABLE `pyscada_globalconfig` ENABLE KEYS */;
UNLOCK TABLES;