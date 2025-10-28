-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `mydb` ;

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8 ;
USE `mydb` ;

-- -----------------------------------------------------
-- Table `mydb`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`users` ;

CREATE TABLE IF NOT EXISTS `mydb`.`users` (
  `user_id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(100) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`tanks`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`tanks` ;

CREATE TABLE IF NOT EXISTS `mydb`.`tanks` (
  `tank_id` INT NOT NULL AUTO_INCREMENT,
  `tank_name` VARCHAR(100) NOT NULL,
  `tank_size` INT NULL,
  `tanks_type` VARCHAR(50) NULL,
  `user_id` INT NOT NULL,
  PRIMARY KEY (`tank_id`, `user_id`),
  INDEX `fk_tanks_users_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_tanks_users`
    FOREIGN KEY (`user_id`)
    REFERENCES `mydb`.`users` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`water_tests`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`water_tests` ;

CREATE TABLE IF NOT EXISTS `mydb`.`water_tests` (
  `water_test_id` INT NOT NULL AUTO_INCREMENT,
  `date_observed` DATE NOT NULL,
  `ammonia` DECIMAL(5,2) NOT NULL,
  `nitrite` DECIMAL(5,2) NOT NULL,
  `nitrate` DECIMAL(5,2) NOT NULL,
  `ph` DECIMAL(4,2) NOT NULL,
  `salinity` DECIMAL(5,2) NULL,
  `temperature` DECIMAL(5,2) NULL,
  `phosphate` DECIMAL(5,2) NULL,
  `calcium` DECIMAL(6,2) NULL,
  `notes` TEXT NULL,
  `tank_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  PRIMARY KEY (`water_test_id`, `tank_id`, `user_id`),
  INDEX `fk_water_tests_tanks1_idx` (`tank_id` ASC, `user_id` ASC) VISIBLE,
  CONSTRAINT `fk_water_tests_tanks1`
    FOREIGN KEY (`tank_id` , `user_id`)
    REFERENCES `mydb`.`tanks` (`tank_id` , `user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
