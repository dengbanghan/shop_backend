CREATE TABLE `orders` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `order_no` varchar(32) NOT NULL,
  `user_id` bigint NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `payment_amount` decimal(10,2) NOT NULL,
  `payment_method` tinyint DEFAULT NULL COMMENT '1-微信, 2-支付宝, 3-京东',
  `payment_time` datetime DEFAULT NULL,
  `status` tinyint DEFAULT '0' COMMENT '0-已提交, 1-待付款, 2-已付款, 3-待发货, 4-已发货, 5-已收货, 6-退款中, 7-退货中, 8-换货中, 9-已完成',
  `shipping_address` text NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_order_no` (`order_no`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;