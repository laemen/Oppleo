--liquibase formatted sql

--changeset: add_primary_key_to_rfid_table
ALTER TABLE public.rfid ADD PRIMARY KEY (rfid);