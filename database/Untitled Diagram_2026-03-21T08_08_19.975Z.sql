CREATE TABLE IF NOT EXISTS `Students` (
	`id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`skills` JSON COMMENT 'JSON - т.к. хранение массивов, которых нет в MySql (но мы все ещё можем поменять диалект sql)',
	`university` VARCHAR(255) NOT NULL COMMENT 'поставила not null, если нет вуза (школьник) пусть будет категория школьник',
	`faculty` VARCHAR(255) COMMENT 'а тут уже наверное можно и пустое поле оставлять, не настолько важная информация',
	`course` TINYINT NOT NULL COMMENT 'хз насчет разделения бакалавриата/магистратуры, возможно стоит сделать VARCHAR',
	`email` VARCHAR(255) NOT NULL UNIQUE CHECK(*@*),
	`phone_number` VARCHAR(255) NOT NULL UNIQUE,
	`tg_id` VARCHAR(255) UNIQUE COMMENT 'допустим, у кого-то нет тг, пусть будет возможность null',
	`tasks_started` JSON COMMENT 'может быть стоит сделать два разных столбца под активные задания и под завершенные',
	`tasks_progressing` JSON,
	`password_hash` VARCHAR(255) NOT NULL,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `Companies` (
	`id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`name` VARCHAR(255) NOT NULL,
	`informatinon` TEXT(65535),
	`projects` JSON NOT NULL COMMENT 'может быть стоит сделать два разных столбца под активные задания и под завершенные',
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `Cases` (
	`id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`organizer_id` INTEGER NOT NULL,
	`performers` JSON COMMENT 'считаем, что один кейс может выполнять одновременно несколько людей, как проверять соотношение человек/кейс будем я пока не понимаю',
	`description` TEXT(65535) NOT NULL,
	`areas` JSON COMMENT 'я ориентируюсь на картинку (https://t.me/c/2553619342/8974/18797)',
	`publication_time` DATE NOT NULL COMMENT 'когда выложили задание',
	`end_time` DATE NOT NULL COMMENT 'дедлайн, возможно у кого-то может быть без него, поэтому с возможностью null',
	PRIMARY KEY(`id`)
);


ALTER TABLE `Companies`
ADD FOREIGN KEY(`id`) REFERENCES `Cases`(`organizer_id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;