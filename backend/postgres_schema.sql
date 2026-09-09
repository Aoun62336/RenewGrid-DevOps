-- PostgreSQL Database Schema for RenewGrid (Reflected from actual DB)
-- This file contains all queries to create the database and tables, and insert sample entries.

-- CREATE DATABASE renewgrid;
-- \c renewgrid;

-- 1. Enum Types
DO $$ BEGIN
    CREATE TYPE pickupstatus AS ENUM ('PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COLLECTED', 'PROCESSING', 'RECYCLED', 'COMPLETED', 'CANCELLED', 'ACCEPTED', 'IN_ROUTE', 'REJECTED', 'DELIVERED', 'PROOF_UPLOADED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE userrole AS ENUM ('USER', 'COLLECTOR', 'RECYCLER', 'ADMIN');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE wastecategory AS ENUM ('LAPTOPS', 'MOBILE', 'MONITORS', 'PRINTERS', 'CIRCUITS', 'BATTERIES', 'MIXED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 2. Tables
CREATE TABLE IF NOT EXISTS users (
	id SERIAL NOT NULL, 
	full_name VARCHAR(150) NOT NULL, 
	email VARCHAR(255) UNIQUE NOT NULL, 
	phone_number VARCHAR(20), 
	address TEXT, 
	profile_image VARCHAR(1000), 
	password_hash VARCHAR(255) NOT NULL, 
	role userrole NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	is_available BOOLEAN NOT NULL, 
	CONSTRAINT users_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS waste_uploads (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	description TEXT, 
	category wastecategory NOT NULL, 
	condition VARCHAR(100), 
	estimated_weight DOUBLE PRECISION NOT NULL, 
	quantity INTEGER NOT NULL, 
	ai_detected_type VARCHAR(255), 
	ai_confidence DOUBLE PRECISION, 
	estimated_price DOUBLE PRECISION, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	estimated_credit_points INTEGER, 
	estimated_co2_saved DOUBLE PRECISION, 
	CONSTRAINT waste_uploads_pkey PRIMARY KEY (id), 
	CONSTRAINT waste_uploads_user_id_fkey FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS waste_images (
	id SERIAL NOT NULL, 
	waste_id INTEGER NOT NULL, 
	image_url VARCHAR(1000) NOT NULL, 
	is_primary BOOLEAN NOT NULL, 
	uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT waste_images_pkey PRIMARY KEY (id), 
	CONSTRAINT waste_images_waste_id_fkey FOREIGN KEY(waste_id) REFERENCES waste_uploads (id)
);

CREATE TABLE IF NOT EXISTS pickup_requests (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	waste_upload_id INTEGER NOT NULL, 
	collector_id INTEGER, 
	address VARCHAR(500) NOT NULL, 
	pickup_date TIMESTAMP WITH TIME ZONE, 
	notes TEXT, 
	status pickupstatus NOT NULL, 
	final_collected_weight DOUBLE PRECISION, 
	collector_notes TEXT, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	latitude DOUBLE PRECISION, 
	longitude DOUBLE PRECISION, 
	recycler_id INTEGER, 
	final_price DOUBLE PRECISION, 
	CONSTRAINT pickup_requests_pkey PRIMARY KEY (id), 
	CONSTRAINT pickup_requests_collector_id_fkey FOREIGN KEY(collector_id) REFERENCES users (id), 
	CONSTRAINT pickup_requests_recycler_id_fkey FOREIGN KEY(recycler_id) REFERENCES users (id), 
	CONSTRAINT pickup_requests_user_id_fkey FOREIGN KEY(user_id) REFERENCES users (id), 
	CONSTRAINT pickup_requests_waste_upload_id_fkey FOREIGN KEY(waste_upload_id) REFERENCES waste_uploads (id)
);

CREATE TABLE IF NOT EXISTS pickup_status_history (
	id SERIAL NOT NULL, 
	pickup_id INTEGER NOT NULL, 
	status pickupstatus NOT NULL, 
	note TEXT, 
	changed_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	changed_by_id INTEGER, 
	CONSTRAINT pickup_status_history_pkey PRIMARY KEY (id), 
	CONSTRAINT pickup_status_history_changed_by_id_fkey FOREIGN KEY(changed_by_id) REFERENCES users (id), 
	CONSTRAINT pickup_status_history_pickup_id_fkey FOREIGN KEY(pickup_id) REFERENCES pickup_requests (id)
);

CREATE TABLE IF NOT EXISTS collector_proofs (
	id SERIAL NOT NULL, 
	pickup_id INTEGER NOT NULL, 
	image_url VARCHAR(1000) NOT NULL, 
	notes TEXT, 
	uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT collector_proofs_pkey PRIMARY KEY (id), 
	CONSTRAINT collector_proofs_pickup_id_fkey FOREIGN KEY(pickup_id) REFERENCES pickup_requests (id), 
	CONSTRAINT collector_proofs_pickup_id_key UNIQUE NULLS DISTINCT (pickup_id)
);

CREATE TABLE IF NOT EXISTS recycler_payments (
	id SERIAL NOT NULL, 
	pickup_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	recycler_id INTEGER NOT NULL, 
	amount DOUBLE PRECISION NOT NULL, 
	waste_item VARCHAR(500), 
	note TEXT, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT recycler_payments_pkey PRIMARY KEY (id), 
	CONSTRAINT recycler_payments_pickup_id_fkey FOREIGN KEY(pickup_id) REFERENCES pickup_requests (id), 
	CONSTRAINT recycler_payments_recycler_id_fkey FOREIGN KEY(recycler_id) REFERENCES users (id), 
	CONSTRAINT recycler_payments_user_id_fkey FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS pricing_rules (
	id SERIAL NOT NULL, 
	category VARCHAR(100) NOT NULL, 
	description TEXT, 
	base_price DOUBLE PRECISION NOT NULL, 
	per_kg_rate DOUBLE PRECISION NOT NULL, 
	premium_rate DOUBLE PRECISION NOT NULL, 
	condition_multiplier_working DOUBLE PRECISION NOT NULL, 
	condition_multiplier_partial DOUBLE PRECISION NOT NULL, 
	condition_multiplier_broken DOUBLE PRECISION NOT NULL, 
	min_weight DOUBLE PRECISION NOT NULL, 
	unit VARCHAR(20) NOT NULL, 
	active BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT pricing_rules_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS pickup_reviews (
	id SERIAL NOT NULL, 
	pickup_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	rating INTEGER NOT NULL, 
	comment TEXT, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT pickup_reviews_pkey PRIMARY KEY (id), 
	CONSTRAINT pickup_reviews_pickup_id_fkey FOREIGN KEY(pickup_id) REFERENCES pickup_requests (id), 
	CONSTRAINT pickup_reviews_user_id_fkey FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS processing_records (
	id SERIAL NOT NULL, 
	pickup_id INTEGER NOT NULL, 
	recycler_id INTEGER NOT NULL, 
	decision VARCHAR(50) NOT NULL, 
	outcome pickupstatus, 
	processing_notes TEXT, 
	revenue_generated DOUBLE PRECISION, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT processing_records_pkey PRIMARY KEY (id), 
	CONSTRAINT processing_records_pickup_id_fkey FOREIGN KEY(pickup_id) REFERENCES pickup_requests (id), 
	CONSTRAINT processing_records_recycler_id_fkey FOREIGN KEY(recycler_id) REFERENCES users (id), 
	CONSTRAINT processing_records_pickup_id_key UNIQUE NULLS DISTINCT (pickup_id)
);

CREATE TABLE IF NOT EXISTS recycler_inventory (
	id SERIAL NOT NULL, 
	recycler_id INTEGER NOT NULL, 
	pickup_id INTEGER NOT NULL, 
	item_description TEXT, 
	weight_kg DOUBLE PRECISION, 
	status VARCHAR(50) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT recycler_inventory_pkey PRIMARY KEY (id), 
	CONSTRAINT recycler_inventory_pickup_id_fkey FOREIGN KEY(pickup_id) REFERENCES pickup_requests (id), 
	CONSTRAINT recycler_inventory_recycler_id_fkey FOREIGN KEY(recycler_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS rewards (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	pickup_id INTEGER NOT NULL, 
	points INTEGER NOT NULL, 
	co2_saved_kg DOUBLE PRECISION NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT rewards_pkey PRIMARY KEY (id), 
	CONSTRAINT rewards_pickup_id_fkey FOREIGN KEY(pickup_id) REFERENCES pickup_requests (id), 
	CONSTRAINT rewards_user_id_fkey FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS notifications (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	message TEXT NOT NULL, 
	is_read BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT notifications_pkey PRIMARY KEY (id), 
	CONSTRAINT notifications_user_id_fkey FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS app_config (
	id SERIAL NOT NULL, 
	key VARCHAR(100) NOT NULL, 
	value TEXT NOT NULL, 
	description TEXT, 
	CONSTRAINT app_config_pkey PRIMARY KEY (id), 
	CONSTRAINT app_config_key_key UNIQUE NULLS DISTINCT (key)
);


-- 3. Seed Data

-- Table: users
INSERT INTO users (id, full_name, email, phone_number, address, profile_image, password_hash, role, is_active, created_at, updated_at, is_available) VALUES (1, 'Mr. Gray', 'admin@renewgrid.com', '9000000001', NULL, '/uploads/profile_images/user_1_e36a3deb8bfe4f9784a6a2dcbe4d7202.png', '$2b$12$QQLbNd9uNl/mPquQc.b5ru0mPhMy6BtcZmteXYIKxbuDuXcZw2Nny', 'ADMIN', true, '2026-05-03 00:32:55.872362+05:30', '2026-05-18 16:12:06.706716+05:30', true) ON CONFLICT (email) DO NOTHING;
INSERT INTO users (id, full_name, email, phone_number, address, profile_image, password_hash, role, is_active, created_at, updated_at, is_available) VALUES (2, 'Aaish ', 'Aaish@renewgrid.com', NULL, NULL, NULL, '$2b$12$UMcuY5Do89c4OpvFtSaD9.urfD1vaLu3CsL5ioS31/9TF4rn4qtFK', 'USER', true, '2026-05-03 12:34:00.798050+05:30', '2026-05-03 12:34:00.798056+05:30', true) ON CONFLICT (email) DO NOTHING;
INSERT INTO users (id, full_name, email, phone_number, address, profile_image, password_hash, role, is_active, created_at, updated_at, is_available) VALUES (3, 'william Wali', 'william@renewgrid.com', NULL, NULL, NULL, '$2b$12$E4TeL91Znn.n7yXDto.dueczUUf.hHEcB6Y6XEeQeLY5e9N7onfAm', 'COLLECTOR', true, '2026-05-03 12:35:02.274729+05:30', '2026-05-03 12:35:02.274733+05:30', true) ON CONFLICT (email) DO NOTHING;
INSERT INTO users (id, full_name, email, phone_number, address, profile_image, password_hash, role, is_active, created_at, updated_at, is_available) VALUES (4, 'Raees Aurangzeb', 'raees@renewgrid.com', NULL, NULL, NULL, '$2b$12$0OkNG49LYoXyshstT87zHuvjz6hzOTBmiYH4.KITqhfuxp2k0gISG', 'RECYCLER', true, '2026-05-03 12:35:54.190872+05:30', '2026-05-03 12:35:54.190876+05:30', true) ON CONFLICT (email) DO NOTHING;
INSERT INTO users (id, full_name, email, phone_number, address, profile_image, password_hash, role, is_active, created_at, updated_at, is_available) VALUES (5, 'Mary Johnson', 'mary@yopmail.com', NULL, NULL, '/uploads/profile_images/user_5_68dd4455b9814777add60d82df88ee46.png', '$2b$12$8mWaCJ9HCIA0X0B9I000l.sSg1lGWY0fhNQOY905A2760qRZ6vV7q', 'RECYCLER', true, '2026-05-12 23:34:28.340292+05:30', '2026-05-18 16:23:46.187328+05:30', true) ON CONFLICT (email) DO NOTHING;
INSERT INTO users (id, full_name, email, phone_number, address, profile_image, password_hash, role, is_active, created_at, updated_at, is_available) VALUES (6, 'Anna Thomas', 'anna@yopmail.com', NULL, NULL, NULL, '$2b$12$e2aEpDK7wc6E1h3z2VyWN.LZRZqTbQHVM3rL/GQG14qz42JIiLblu', 'USER', true, '2026-05-12 23:55:00.890968+05:30', '2026-05-12 23:55:00.890973+05:30', true) ON CONFLICT (email) DO NOTHING;
INSERT INTO users (id, full_name, email, phone_number, address, profile_image, password_hash, role, is_active, created_at, updated_at, is_available) VALUES (7, 'John Matthew', 'john@yopmail.com', NULL, NULL, NULL, '$2b$12$3Z1GZCypfb6yiLeEDkGwf.r7jy99yLBOU7j/5W1vuW0Gj1vsC0VOi', 'USER', true, '2026-05-12 23:55:49.154092+05:30', '2026-05-12 23:55:49.154096+05:30', true) ON CONFLICT (email) DO NOTHING;
INSERT INTO users (id, full_name, email, phone_number, address, profile_image, password_hash, role, is_active, created_at, updated_at, is_available) VALUES (8, 'Paul Thomas', 'paul@yopmail.com', NULL, NULL, '/uploads/profile_images/user_8_e90a7aaab7b949c7a93a972a67a244a0.png', '$2b$12$51zoTKenT2sE6CjvmZ4xjuRW/4DqLu/Idz/DW75bRsRfPb1nb43oe', 'COLLECTOR', true, '2026-05-12 23:56:50.999947+05:30', '2026-05-18 16:19:16.815799+05:30', true) ON CONFLICT (email) DO NOTHING;
INSERT INTO users (id, full_name, email, phone_number, address, profile_image, password_hash, role, is_active, created_at, updated_at, is_available) VALUES (9, 'Peter Samuel', 'peter@yopmail.com', NULL, NULL, NULL, '$2b$12$29JKznWlLgdmshkV9chaRek42hPE3ul7tw3U0YuCN8isROmcfF.XW', 'COLLECTOR', true, '2026-05-12 23:58:54.346311+05:30', '2026-05-12 23:58:54.346319+05:30', true) ON CONFLICT (email) DO NOTHING;
INSERT INTO users (id, full_name, email, phone_number, address, profile_image, password_hash, role, is_active, created_at, updated_at, is_available) VALUES (10, 'Grace Wilson', 'grace@yopmail.com', NULL, NULL, NULL, '$2b$12$6vRDio987HBo4wRxkl9j.urQB9c7sC41YWSVejY9.ZiYy.3XF/Zr2', 'RECYCLER', true, '2026-05-13 00:00:26.920380+05:30', '2026-05-13 00:00:26.920385+05:30', true) ON CONFLICT (email) DO NOTHING;
INSERT INTO users (id, full_name, email, phone_number, address, profile_image, password_hash, role, is_active, created_at, updated_at, is_available) VALUES (11, 'Ruth Daniel', 'ruth@yopmail.com', NULL, NULL, NULL, '$2b$12$OeXQZMt5ZhciwMl.pTg9/e5d3X2sAdqVfFdwx/fJdCYadKHdcJv.2', 'USER', true, '2026-05-13 00:02:02.937745+05:30', '2026-05-13 00:02:02.937750+05:30', true) ON CONFLICT (email) DO NOTHING;

-- Table: waste_uploads
INSERT INTO waste_uploads (id, user_id, title, description, category, condition, estimated_weight, quantity, ai_detected_type, ai_confidence, estimated_price, created_at, updated_at, estimated_credit_points, estimated_co2_saved) VALUES (1, 2, 'refrigerator ', NULL, 'MIXED', 'Damaged', 7.8, 1, 'AI: WasteCategory.MIXED', 0.8, 186.0, '2026-05-03 13:56:30.565036+05:30', '2026-05-03 13:56:30.565043+05:30', NULL, NULL);
INSERT INTO waste_uploads (id, user_id, title, description, category, condition, estimated_weight, quantity, ai_detected_type, ai_confidence, estimated_price, created_at, updated_at, estimated_credit_points, estimated_co2_saved) VALUES (3, 2, 'poco phone ', NULL, 'MOBILE', 'Working', 0.5, 1, 'AI: WasteCategory.MOBILE', 0.95, 180.0, '2026-05-05 15:56:28.520122+05:30', '2026-05-05 15:56:28.520130+05:30', NULL, NULL);
INSERT INTO waste_uploads (id, user_id, title, description, category, condition, estimated_weight, quantity, ai_detected_type, ai_confidence, estimated_price, created_at, updated_at, estimated_credit_points, estimated_co2_saved) VALUES (4, 2, 'poco', NULL, 'MOBILE', 'Working', -0.1, 1, 'AI: WasteCategory.MOBILE', 0.95, 60.0, '2026-05-05 16:54:08.970702+05:30', '2026-05-05 16:54:08.970709+05:30', NULL, NULL);
INSERT INTO waste_uploads (id, user_id, title, description, category, condition, estimated_weight, quantity, ai_detected_type, ai_confidence, estimated_price, created_at, updated_at, estimated_credit_points, estimated_co2_saved) VALUES (5, 2, 'phone', NULL, 'MOBILE', 'Partially Working', 0.5, 1, 'AI: WasteCategory.MOBILE', 0.95, 180.0, '2026-05-05 16:58:10.124563+05:30', '2026-05-05 16:58:10.124576+05:30', NULL, NULL);
INSERT INTO waste_uploads (id, user_id, title, description, category, condition, estimated_weight, quantity, ai_detected_type, ai_confidence, estimated_price, created_at, updated_at, estimated_credit_points, estimated_co2_saved) VALUES (6, 2, 'refrigeretor', NULL, 'MIXED', 'Damaged', 8.0, 1, 'AI: WasteCategory.MIXED', 0.8, 190.0, '2026-05-06 15:09:49.661279+05:30', '2026-05-06 15:09:49.661286+05:30', NULL, NULL);
INSERT INTO waste_uploads (id, user_id, title, description, category, condition, estimated_weight, quantity, ai_detected_type, ai_confidence, estimated_price, created_at, updated_at, estimated_credit_points, estimated_co2_saved) VALUES (7, 2, 'phone', NULL, 'MOBILE', 'Partially Working', 0.5, 1, 'AI: WasteCategory.MOBILE', 0.95, 1025.0, '2026-05-09 12:32:22.724290+05:30', '2026-05-09 12:32:22.724295+05:30', NULL, NULL);
INSERT INTO waste_uploads (id, user_id, title, description, category, condition, estimated_weight, quantity, ai_detected_type, ai_confidence, estimated_price, created_at, updated_at, estimated_credit_points, estimated_co2_saved) VALUES (8, 2, 'battery', 'this battery is non functional but looks working', 'BATTERIES', 'Non-functional', 0.8, 1, 'AI: WasteCategory.BATTERIES', 0.9, 98.0, '2026-05-12 11:44:48.066208+05:30', '2026-05-12 11:44:48.066217+05:30', NULL, NULL);
INSERT INTO waste_uploads (id, user_id, title, description, category, condition, estimated_weight, quantity, ai_detected_type, ai_confidence, estimated_price, created_at, updated_at, estimated_credit_points, estimated_co2_saved) VALUES (9, 6, 'phone', 'back glass broken', 'MOBILE', 'Working', 0.156, 1, 'AI: WasteCategory.MOBILE', 0.93, 531.2, '2026-05-18 14:50:00.803933+05:30', '2026-05-18 14:50:00.803941+05:30', 1, 0.08);
INSERT INTO waste_uploads (id, user_id, title, description, category, condition, estimated_weight, quantity, ai_detected_type, ai_confidence, estimated_price, created_at, updated_at, estimated_credit_points, estimated_co2_saved) VALUES (10, 6, 'samsung phone', 'everything good', 'MOBILE', 'Working', 0.151, 1, 'AI: WasteCategory.MOBILE', 0.93, 6575.5, '2026-05-18 15:05:20.674157+05:30', '2026-05-18 15:05:20.674164+05:30', 1, 0.08);
INSERT INTO waste_uploads (id, user_id, title, description, category, condition, estimated_weight, quantity, ai_detected_type, ai_confidence, estimated_price, created_at, updated_at, estimated_credit_points, estimated_co2_saved) VALUES (11, 6, 'ac', 'good', 'MIXED', 'Working', 10.0, 1, 'AI: WasteCategory.MIXED', 0.93, 1900.0, '2026-05-18 15:08:07.037650+05:30', '2026-05-18 15:08:07.037655+05:30', 100, 5.0);
INSERT INTO waste_uploads (id, user_id, title, description, category, condition, estimated_weight, quantity, ai_detected_type, ai_confidence, estimated_price, created_at, updated_at, estimated_credit_points, estimated_co2_saved) VALUES (12, 6, 'loq laptop', 'excellent new condition', 'LAPTOPS', 'Working', 2.3, 1, 'AI: WasteCategory.LAPTOPS', 0.93, 9150.0, '2026-05-18 15:13:54.135203+05:30', '2026-05-18 15:13:54.135210+05:30', 23, 1.15);
INSERT INTO waste_uploads (id, user_id, title, description, category, condition, estimated_weight, quantity, ai_detected_type, ai_confidence, estimated_price, created_at, updated_at, estimated_credit_points, estimated_co2_saved) VALUES (13, 6, 'ac', 'excellent condition', 'MIXED', 'Working', 12.0, 1, 'AI: WasteCategory.MIXED', 0.93, 2200.0, '2026-05-18 15:19:31.050929+05:30', '2026-05-18 15:19:31.050934+05:30', 120, 6.0);

-- Table: waste_images
INSERT INTO waste_images (id, waste_id, image_url, is_primary, uploaded_at) VALUES (1, 1, '/uploads/waste/93b8f77677104b2b8a1cb9ba4243d12a.png', true, '2026-05-03 13:56:30.590082+05:30');
INSERT INTO waste_images (id, waste_id, image_url, is_primary, uploaded_at) VALUES (3, 3, '/uploads/waste/d33847af318441e2a830a3bdfe426519.jpeg', true, '2026-05-05 15:56:28.544028+05:30');
INSERT INTO waste_images (id, waste_id, image_url, is_primary, uploaded_at) VALUES (4, 4, '/uploads/waste/1ab7af1c3d1f48bfb5355edaad6de9bc.jpeg', true, '2026-05-05 16:54:08.979325+05:30');
INSERT INTO waste_images (id, waste_id, image_url, is_primary, uploaded_at) VALUES (5, 5, '/uploads/waste/c0c99429ebc14deca9aec30f19c324a1.jpeg', true, '2026-05-05 16:58:10.130746+05:30');
INSERT INTO waste_images (id, waste_id, image_url, is_primary, uploaded_at) VALUES (6, 6, '/uploads/waste/aacebdbd704b4e9d816570d136aac47c.png', true, '2026-05-06 15:09:49.704343+05:30');
INSERT INTO waste_images (id, waste_id, image_url, is_primary, uploaded_at) VALUES (7, 7, '/uploads/waste/60783f5473fb410f9ecfb6e9a0dc38f3.jpeg', true, '2026-05-09 12:32:22.746808+05:30');
INSERT INTO waste_images (id, waste_id, image_url, is_primary, uploaded_at) VALUES (8, 8, '/uploads/waste/e3e25037efa74134b3b6ff9a7e04bd60.jpeg', true, '2026-05-12 11:44:48.090006+05:30');
INSERT INTO waste_images (id, waste_id, image_url, is_primary, uploaded_at) VALUES (9, 9, '/uploads/waste/e57683193fba47bd97e2e84fc7e07c0f.jpeg', true, '2026-05-18 14:50:00.834778+05:30');
INSERT INTO waste_images (id, waste_id, image_url, is_primary, uploaded_at) VALUES (10, 10, '/uploads/waste/9ec201e3c76e4126b9d2b231042747c4.jpeg', true, '2026-05-18 15:05:20.685631+05:30');
INSERT INTO waste_images (id, waste_id, image_url, is_primary, uploaded_at) VALUES (11, 11, '/uploads/waste/3418a2b1430c4360bd98df62bb96f3b4.jpeg', true, '2026-05-18 15:08:07.041549+05:30');
INSERT INTO waste_images (id, waste_id, image_url, is_primary, uploaded_at) VALUES (12, 12, '/uploads/waste/9fcb1d79cd8045df91f02d73f8a2cf57.jpeg', true, '2026-05-18 15:13:54.143983+05:30');
INSERT INTO waste_images (id, waste_id, image_url, is_primary, uploaded_at) VALUES (13, 12, '/uploads/waste/3c022da63c044c56b6ff3ae7a0d56db8.jpeg', false, '2026-05-18 15:13:54.143992+05:30');
INSERT INTO waste_images (id, waste_id, image_url, is_primary, uploaded_at) VALUES (14, 13, '/uploads/waste/5330cc5779a04f55adafdc4c0f06d2a3.jpeg', true, '2026-05-18 15:19:31.055727+05:30');

-- Table: pickup_requests
INSERT INTO pickup_requests (id, user_id, waste_upload_id, collector_id, address, pickup_date, notes, status, final_collected_weight, collector_notes, created_at, updated_at, latitude, longitude, recycler_id, final_price) VALUES (1, 2, 1, 3, 'H.No.200 qilla malegaon nashik, malegaon,nashik, 423203', '2026-05-05 10:30:00+05:30', NULL, 'COMPLETED', 8.0, NULL, '2026-05-03 13:58:03.730607+05:30', '2026-05-03 14:13:43.253627+05:30', NULL, NULL, 4, NULL);
INSERT INTO pickup_requests (id, user_id, waste_upload_id, collector_id, address, pickup_date, notes, status, final_collected_weight, collector_notes, created_at, updated_at, latitude, longitude, recycler_id, final_price) VALUES (3, 2, 3, 3, 'H.No.200,Qilla,Near Maharashtra bank Malegaon, Malegaon Nashik, 423203', '2026-05-28 16:30:00+05:30', NULL, 'RECYCLED', 0.3, NULL, '2026-05-05 15:56:45.047242+05:30', '2026-05-05 16:39:54.635697+05:30', NULL, NULL, 4, NULL);
INSERT INTO pickup_requests (id, user_id, waste_upload_id, collector_id, address, pickup_date, notes, status, final_collected_weight, collector_notes, created_at, updated_at, latitude, longitude, recycler_id, final_price) VALUES (4, 2, 5, 3, 'H.No.200,Qilla,Near Maharashtra bank Malegaon, Malegaon Nashik, 423203', '2026-05-01 13:30:00+05:30', NULL, 'COMPLETED', 0.5, NULL, '2026-05-05 17:00:06.197108+05:30', '2026-05-12 12:15:19.384882+05:30', NULL, NULL, 4, 360.0);
INSERT INTO pickup_requests (id, user_id, waste_upload_id, collector_id, address, pickup_date, notes, status, final_collected_weight, collector_notes, created_at, updated_at, latitude, longitude, recycler_id, final_price) VALUES (5, 2, 6, 3, 'H.No.200,Qilla,Near Maharashtra bank Malegaon, Malegaon Nashik, 423203', '2026-05-13 13:30:00+05:30', NULL, 'RECYCLED', 8.0, NULL, '2026-05-06 15:10:40.099556+05:30', '2026-05-06 15:21:31.296070+05:30', NULL, NULL, 4, NULL);
INSERT INTO pickup_requests (id, user_id, waste_upload_id, collector_id, address, pickup_date, notes, status, final_collected_weight, collector_notes, created_at, updated_at, latitude, longitude, recycler_id, final_price) VALUES (6, 6, 13, 8, 'kusmuba road, near KGN hospital, Malegaon, 423203', '2026-05-20 12:00:00+05:30', NULL, 'COMPLETED', 9.5, NULL, '2026-05-18 15:22:21.588029+05:30', '2026-05-18 16:22:25.018071+05:30', NULL, NULL, 5, 1825.0);

-- Table: pickup_status_history
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (1, 1, 'PENDING', 'Pickup request created', '2026-05-03 13:58:03.736325+05:30', 2);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (2, 1, 'ACCEPTED', 'Collector accepted the assignment', '2026-05-03 14:10:41.376422+05:30', 3);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (3, 1, 'IN_PROGRESS', 'Collector reached pickup location', '2026-05-03 14:12:35.130159+05:30', 3);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (4, 1, 'COLLECTED', 'Waste collected from user', '2026-05-03 14:13:40.743140+05:30', 3);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (5, 1, 'COMPLETED', 'Waste handed over to recycler', '2026-05-03 14:13:43.254941+05:30', 3);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (13, 3, 'PENDING', 'Pickup request created', '2026-05-05 15:56:45.053802+05:30', 2);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (14, 3, 'IN_PROGRESS', 'Collector accepted & started processing', '2026-05-05 15:57:59.922438+05:30', 3);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (15, 3, 'PROOF_UPLOADED', 'Collector uploaded proof image', '2026-05-05 16:09:42.891282+05:30', 3);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (16, 3, 'COLLECTED', 'Waste marked as Collected', '2026-05-05 16:09:48.495955+05:30', 3);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (17, 3, 'DELIVERED', 'Handed over to Recycler', '2026-05-05 16:09:51.844992+05:30', 3);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (18, 3, 'PROCESSING', 'Processing started: pending_ai', '2026-05-05 16:39:37.553892+05:30', 4);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (19, 3, 'RECYCLED', 'Outcome: PickupStatus.RECYCLED', '2026-05-05 16:39:54.637674+05:30', 4);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (20, 4, 'PENDING', 'Pickup request created', '2026-05-05 17:00:06.205794+05:30', 2);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (21, 5, 'PENDING', 'Pickup request created', '2026-05-06 15:10:40.108171+05:30', 2);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (22, 5, 'IN_PROGRESS', 'Collector accepted & started processing', '2026-05-06 15:18:30.509019+05:30', 3);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (23, 5, 'PROOF_UPLOADED', 'Collector uploaded proof image', '2026-05-06 15:19:34.708487+05:30', 3);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (24, 5, 'COLLECTED', 'Waste marked as Collected', '2026-05-06 15:19:40.014320+05:30', 3);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (25, 5, 'DELIVERED', 'Handed over to Recycler', '2026-05-06 15:19:49.118263+05:30', 3);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (26, 5, 'PROCESSING', 'Processing started: pending_ai', '2026-05-06 15:20:33.952141+05:30', 4);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (27, 5, 'RECYCLED', 'Outcome: PickupStatus.RECYCLED', '2026-05-06 15:21:31.297592+05:30', 4);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (28, 4, 'IN_PROGRESS', 'Collector accepted & started processing', '2026-05-12 12:12:31.062181+05:30', 3);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (29, 4, 'PROOF_UPLOADED', 'Collector uploaded proof image', '2026-05-12 12:13:42.082581+05:30', 3);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (30, 4, 'COLLECTED', 'Waste marked as Collected', '2026-05-12 12:13:46.186978+05:30', 3);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (31, 4, 'DELIVERED', 'Handed over to Recycler', '2026-05-12 12:13:48.153848+05:30', 3);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (32, 4, 'PROCESSING', 'Processing started: pending_ai', '2026-05-12 12:14:28.116338+05:30', 4);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (33, 4, 'COMPLETED', 'Outcome: PickupStatus.COMPLETED', '2026-05-12 12:15:19.386307+05:30', 4);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (34, 6, 'PENDING', 'Pickup request created', '2026-05-18 15:22:21.595980+05:30', 6);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (35, 6, 'IN_PROGRESS', 'Collector accepted & started processing', '2026-05-18 16:15:34.882657+05:30', 8);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (36, 6, 'PROOF_UPLOADED', 'Collector uploaded proof image', '2026-05-18 16:16:34.317122+05:30', 8);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (37, 6, 'COLLECTED', 'Waste marked as Collected', '2026-05-18 16:16:41.047689+05:30', 8);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (38, 6, 'DELIVERED', 'Handed over to Recycler', '2026-05-18 16:16:45.264981+05:30', 8);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (39, 6, 'PROCESSING', 'Processing started: pending_ai', '2026-05-18 16:21:22.167304+05:30', 5);
INSERT INTO pickup_status_history (id, pickup_id, status, note, changed_at, changed_by_id) VALUES (40, 6, 'COMPLETED', 'Outcome: PickupStatus.COMPLETED', '2026-05-18 16:22:25.018997+05:30', 5);

-- Table: collector_proofs
INSERT INTO collector_proofs (id, pickup_id, image_url, notes, uploaded_at) VALUES (1, 1, '/uploads/proofs/d379067494a94e64bf079b5699b036b5.png', NULL, '2026-05-03 14:13:33.483807+05:30');
INSERT INTO collector_proofs (id, pickup_id, image_url, notes, uploaded_at) VALUES (3, 3, '/uploads/proofs/af8953acec5648f785955b8526c8f25a.jpeg', NULL, '2026-05-05 16:09:42.883533+05:30');
INSERT INTO collector_proofs (id, pickup_id, image_url, notes, uploaded_at) VALUES (4, 5, '/uploads/proofs/6c0e935780db4bd3ac89f85c4acab543.png', NULL, '2026-05-06 15:19:34.704117+05:30');
INSERT INTO collector_proofs (id, pickup_id, image_url, notes, uploaded_at) VALUES (5, 4, '/uploads/proofs/cdf70a05402046a7bb6ba78ef4c877b9.jpeg', 'phone received properly ', '2026-05-12 12:13:42.078738+05:30');
INSERT INTO collector_proofs (id, pickup_id, image_url, notes, uploaded_at) VALUES (6, 6, '/uploads/proofs/e4b7f8fb78a848e2b74189974acaeb60.jpeg', 'just weight is different than the original uploaded', '2026-05-18 16:16:34.313770+05:30');

-- Table: recycler_payments
INSERT INTO recycler_payments (id, pickup_id, user_id, recycler_id, amount, waste_item, note, created_at) VALUES (2, 3, 2, 4, 149.85, 'poco phone ', NULL, '2026-05-05 16:39:46.259102+05:30');
INSERT INTO recycler_payments (id, pickup_id, user_id, recycler_id, amount, waste_item, note, created_at) VALUES (3, 5, 2, 4, 170.01, 'refrigeretor', NULL, '2026-05-06 15:21:14.896111+05:30');
INSERT INTO recycler_payments (id, pickup_id, user_id, recycler_id, amount, waste_item, note, created_at) VALUES (4, 4, 2, 4, 208.19, 'phone', NULL, '2026-05-12 12:14:52.950295+05:30');
INSERT INTO recycler_payments (id, pickup_id, user_id, recycler_id, amount, waste_item, note, created_at) VALUES (5, 6, 6, 5, 2200.0, 'ac', 'your acs'' weight was less than the said', '2026-05-18 16:22:15.081354+05:30');

-- Table: pricing_rules
INSERT INTO pricing_rules (id, category, description, base_price, per_kg_rate, premium_rate, condition_multiplier_working, condition_multiplier_partial, condition_multiplier_broken, min_weight, unit, active, created_at, updated_at) VALUES (1, 'Laptops & Computers', 'Laptops, desktops, servers', 8000.0, 500.0, 1000.0, 1.0, 0.6, 0.3, 0.5, 'kg', true, '2026-05-12 11:46:41.852884+05:30', '2026-05-18 15:01:36.201974+05:30');
INSERT INTO pricing_rules (id, category, description, base_price, per_kg_rate, premium_rate, condition_multiplier_working, condition_multiplier_partial, condition_multiplier_broken, min_weight, unit, active, created_at, updated_at) VALUES (2, 'Mobile Phones', 'Smartphones, feature phones, tablets', 6500.0, 500.0, 1500.0, 1.0, 0.5, 0.25, 0.1, 'kg', true, '2026-05-12 11:46:41.852895+05:30', '2026-05-18 15:01:36.201979+05:30');
INSERT INTO pricing_rules (id, category, description, base_price, per_kg_rate, premium_rate, condition_multiplier_working, condition_multiplier_partial, condition_multiplier_broken, min_weight, unit, active, created_at, updated_at) VALUES (3, 'Circuit Boards', 'PCBs, motherboards, GPUs, RAM modules', 1000.0, 1500.0, 2000.0, 1.0, 0.7, 0.4, 0.2, 'kg', true, '2026-05-12 11:46:41.852898+05:30', '2026-05-18 15:01:36.201980+05:30');
INSERT INTO pricing_rules (id, category, description, base_price, per_kg_rate, premium_rate, condition_multiplier_working, condition_multiplier_partial, condition_multiplier_broken, min_weight, unit, active, created_at, updated_at) VALUES (4, 'Batteries', 'Li-ion, NiMH, lead-acid batteries', 300.0, 250.0, 500.0, 1.0, 0.5, 0.2, 0.1, 'kg', true, '2026-05-12 11:46:41.852901+05:30', '2026-05-18 15:01:36.201981+05:30');
INSERT INTO pricing_rules (id, category, description, base_price, per_kg_rate, premium_rate, condition_multiplier_working, condition_multiplier_partial, condition_multiplier_broken, min_weight, unit, active, created_at, updated_at) VALUES (5, 'Monitors & Displays', 'LCD, LED, CRT monitors', 1200.0, 150.0, 300.0, 1.0, 0.5, 0.2, 1.0, 'kg', true, '2026-05-12 11:46:41.852904+05:30', '2026-05-18 15:01:36.201981+05:30');
INSERT INTO pricing_rules (id, category, description, base_price, per_kg_rate, premium_rate, condition_multiplier_working, condition_multiplier_partial, condition_multiplier_broken, min_weight, unit, active, created_at, updated_at) VALUES (6, 'Printers & Peripherals', 'Printers, scanners, keyboards, mice', 800.0, 100.0, 250.0, 1.0, 0.5, 0.2, 0.5, 'kg', true, '2026-05-12 11:46:41.852907+05:30', '2026-05-18 15:01:36.201982+05:30');
INSERT INTO pricing_rules (id, category, description, base_price, per_kg_rate, premium_rate, condition_multiplier_working, condition_multiplier_partial, condition_multiplier_broken, min_weight, unit, active, created_at, updated_at) VALUES (7, 'Mixed Electronics', 'Assorted electronic waste', 400.0, 150.0, 200.0, 1.0, 0.5, 0.2, 0.5, 'kg', true, '2026-05-12 11:46:41.852909+05:30', '2026-05-18 15:01:36.201983+05:30');

-- Table: pickup_reviews
INSERT INTO pickup_reviews (id, pickup_id, user_id, rating, comment, created_at) VALUES (1, 1, 2, 4, 'best services ', '2026-05-04 13:35:55.173557+05:30');

-- Table: processing_records
INSERT INTO processing_records (id, pickup_id, recycler_id, decision, outcome, processing_notes, revenue_generated, created_at, updated_at) VALUES (2, 3, 4, 'recycle', 'RECYCLED', 'Receipt Confirmed', 149.85, '2026-05-05 16:39:37.530165+05:30', '2026-05-12 12:52:07.177956+05:30');
INSERT INTO processing_records (id, pickup_id, recycler_id, decision, outcome, processing_notes, revenue_generated, created_at, updated_at) VALUES (3, 5, 4, 'recycle', 'RECYCLED', 'Receipt Confirmed', 170.01, '2026-05-06 15:20:33.943179+05:30', '2026-05-12 12:52:07.177961+05:30');
INSERT INTO processing_records (id, pickup_id, recycler_id, decision, outcome, processing_notes, revenue_generated, created_at, updated_at) VALUES (4, 4, 4, 'refurbish', 'COMPLETED', 'the given item need to be refurbish ', 208.19, '2026-05-12 12:14:28.106511+05:30', '2026-05-12 12:52:07.177962+05:30');
INSERT INTO processing_records (id, pickup_id, recycler_id, decision, outcome, processing_notes, revenue_generated, created_at, updated_at) VALUES (5, 6, 5, 'refurbish', 'COMPLETED', 'Receipt Confirmed', NULL, '2026-05-18 16:21:22.162231+05:30', '2026-05-18 16:22:25.020279+05:30');

-- Table: recycler_inventory
INSERT INTO recycler_inventory (id, recycler_id, pickup_id, item_description, weight_kg, status, created_at) VALUES (1, 4, 3, NULL, 0.3, 'recycled', '2026-05-05 16:39:54.641932+05:30');
INSERT INTO recycler_inventory (id, recycler_id, pickup_id, item_description, weight_kg, status, created_at) VALUES (2, 4, 5, NULL, 8.0, 'recycled', '2026-05-06 15:21:31.303252+05:30');
INSERT INTO recycler_inventory (id, recycler_id, pickup_id, item_description, weight_kg, status, created_at) VALUES (3, 4, 4, NULL, 0.5, 'completed', '2026-05-12 12:15:19.392912+05:30');
INSERT INTO recycler_inventory (id, recycler_id, pickup_id, item_description, weight_kg, status, created_at) VALUES (4, 5, 6, NULL, 9.5, 'completed', '2026-05-18 16:22:25.021605+05:30');

-- Table: rewards
INSERT INTO rewards (id, user_id, pickup_id, points, co2_saved_kg, created_at) VALUES (1, 2, 4, 5, 0.25, '2026-05-12 12:15:19.431878+05:30');
INSERT INTO rewards (id, user_id, pickup_id, points, co2_saved_kg, created_at) VALUES (2, 6, 6, 95, 4.75, '2026-05-18 16:22:25.045508+05:30');

-- Table: notifications
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (1, 2, 'Waste Uploaded Successfully', 'Your waste upload #1 has been recorded and is awaiting review.', true, '2026-05-03 13:56:30.613552+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (2, 2, 'Pickup Assigned', 'Your pickup request #1 has been assigned to a collector.', true, '2026-05-03 14:00:29.701014+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (3, 3, 'New Pickup Assigned', 'You have been assigned to pickup request #1 at H.No.200 qilla malegaon nashik, malegaon,nashik, 423203.', true, '2026-05-03 14:00:29.704983+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (4, 2, 'Waste Uploaded Successfully', 'Your waste upload #2 has been recorded and is awaiting review.', true, '2026-05-04 13:34:07.696956+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (5, 2, 'Pickup Assigned', 'Your pickup request #2 has been assigned to a collector.', true, '2026-05-04 13:36:31.214522+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (6, 3, 'New Pickup Assigned', 'You have been assigned to pickup request #2 at H.No.500,naya isla,mpura, Near nishat school Malegaon, Malegaon Nashik, 423203.', true, '2026-05-04 13:36:31.216842+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (7, 2, 'Waste Uploaded Successfully', 'Your waste upload #3 has been recorded and is awaiting review.', true, '2026-05-05 15:56:28.560901+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (8, 2, 'Pickup Assigned', 'Your pickup request #3 has been assigned to a collector.', true, '2026-05-05 15:57:19.734540+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (9, 3, 'New Pickup Assigned', 'You have been assigned to pickup request #3 at H.No.200,Qilla,Near Maharashtra bank Malegaon, Malegaon Nashik, 423203.', false, '2026-05-05 15:57:19.740635+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (10, 2, 'Waste Uploaded Successfully', 'Your waste upload #4 has been recorded and is awaiting review.', true, '2026-05-05 16:54:08.998518+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (11, 2, 'Waste Uploaded Successfully', 'Your waste upload #5 has been recorded and is awaiting review.', true, '2026-05-05 16:58:10.154841+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (12, 2, 'Waste Uploaded Successfully', 'Your waste upload #6 has been recorded and is awaiting review.', true, '2026-05-06 15:09:49.722637+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (13, 2, 'Pickup Assigned', 'Your pickup request #5 has been assigned to a collector.', true, '2026-05-06 15:15:31.549700+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (14, 3, 'New Pickup Assigned', 'You have been assigned to pickup request #5 at H.No.200,Qilla,Near Maharashtra bank Malegaon, Malegaon Nashik, 423203.', false, '2026-05-06 15:15:31.556298+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (15, 2, 'Waste Uploaded Successfully', 'Your waste upload #7 has been recorded and is awaiting review.', true, '2026-05-09 12:32:22.762299+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (16, 2, 'Waste Uploaded Successfully', 'Your waste upload #8 has been recorded and is awaiting review.', false, '2026-05-12 11:44:48.111738+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (17, 2, 'Pickup Assigned', 'Your pickup request #4 has been assigned to a collector.', false, '2026-05-12 12:11:52.834864+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (18, 3, 'New Pickup Assigned', 'You have been assigned to pickup request #4 at H.No.200,Qilla,Near Maharashtra bank Malegaon, Malegaon Nashik, 423203.', false, '2026-05-12 12:11:52.841260+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (19, 2, 'Pickup Completed', 'Your pickup request #4 has been successfully completed!', false, '2026-05-12 12:15:19.420419+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (20, 2, 'Reward Generated', 'You''ve earned 5 points and saved 0.25 kg of CO₂ for pickup #4!', false, '2026-05-12 12:15:19.428657+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (21, 6, 'Waste Uploaded Successfully', 'Your waste upload #9 has been recorded and is awaiting review.', false, '2026-05-18 14:50:00.864462+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (22, 6, 'Waste Uploaded Successfully', 'Your waste upload #10 has been recorded and is awaiting review.', false, '2026-05-18 15:05:20.697009+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (23, 6, 'Waste Uploaded Successfully', 'Your waste upload #11 has been recorded and is awaiting review.', false, '2026-05-18 15:08:07.049039+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (24, 6, 'Waste Uploaded Successfully', 'Your waste upload #12 has been recorded and is awaiting review.', false, '2026-05-18 15:13:54.155919+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (25, 6, 'Waste Uploaded Successfully', 'Your waste upload #13 has been recorded and is awaiting review.', false, '2026-05-18 15:19:31.066443+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (26, 6, 'Pickup Assigned', 'Your pickup request #6 has been assigned to a collector.', false, '2026-05-18 15:33:55.733785+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (27, 8, 'New Pickup Assigned', 'You have been assigned to pickup request #6 at kusmuba road, near KGN hospital, Malegaon, 423203.', false, '2026-05-18 15:33:55.736992+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (28, 6, 'Pickup Completed', 'Your pickup request #6 has been successfully completed!', false, '2026-05-18 16:22:25.035140+05:30');
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES (29, 6, 'Reward Generated', 'You''ve earned 95 points and saved 4.75 kg of CO₂ for pickup #6!', false, '2026-05-18 16:22:25.042154+05:30');



-- 4. Reset Sequences (to avoid primary key conflicts with serial ids)
SELECT setval(pg_get_serial_sequence('users', 'id'), coalesce(max(id), 1)) FROM users;
SELECT setval(pg_get_serial_sequence('waste_uploads', 'id'), coalesce(max(id), 1)) FROM waste_uploads;
SELECT setval(pg_get_serial_sequence('waste_images', 'id'), coalesce(max(id), 1)) FROM waste_images;
SELECT setval(pg_get_serial_sequence('pickup_requests', 'id'), coalesce(max(id), 1)) FROM pickup_requests;
SELECT setval(pg_get_serial_sequence('pickup_status_history', 'id'), coalesce(max(id), 1)) FROM pickup_status_history;
SELECT setval(pg_get_serial_sequence('collector_proofs', 'id'), coalesce(max(id), 1)) FROM collector_proofs;
SELECT setval(pg_get_serial_sequence('recycler_payments', 'id'), coalesce(max(id), 1)) FROM recycler_payments;
SELECT setval(pg_get_serial_sequence('pricing_rules', 'id'), coalesce(max(id), 1)) FROM pricing_rules;
SELECT setval(pg_get_serial_sequence('pickup_reviews', 'id'), coalesce(max(id), 1)) FROM pickup_reviews;
SELECT setval(pg_get_serial_sequence('processing_records', 'id'), coalesce(max(id), 1)) FROM processing_records;
SELECT setval(pg_get_serial_sequence('recycler_inventory', 'id'), coalesce(max(id), 1)) FROM recycler_inventory;
SELECT setval(pg_get_serial_sequence('rewards', 'id'), coalesce(max(id), 1)) FROM rewards;
SELECT setval(pg_get_serial_sequence('notifications', 'id'), coalesce(max(id), 1)) FROM notifications;
SELECT setval(pg_get_serial_sequence('app_config', 'id'), coalesce(max(id), 1)) FROM app_config;
