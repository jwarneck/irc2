--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'SQL_ASCII';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: messages; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE messages (
    msg_id bigint NOT NULL,
    content character varying(250) NOT NULL,
    poster character varying(20)
);


ALTER TABLE public.messages OWNER TO postgres;

--
-- Name: messages_msg_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE messages_msg_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.messages_msg_id_seq OWNER TO postgres;

--
-- Name: messages_msg_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE messages_msg_id_seq OWNED BY messages.msg_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE users (
    username character varying(20) NOT NULL,
    password character varying(100) NOT NULL,
    key_column bigint NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_key_column_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE users_key_column_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_key_column_seq OWNER TO postgres;

--
-- Name: users_key_column_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE users_key_column_seq OWNED BY users.key_column;


--
-- Name: msg_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY messages ALTER COLUMN msg_id SET DEFAULT nextval('messages_msg_id_seq'::regclass);


--
-- Name: key_column; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users ALTER COLUMN key_column SET DEFAULT nextval('users_key_column_seq'::regclass);


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY messages (msg_id, content, poster) FROM stdin;
1	Hello	test
2	Now?	test
3	This should be working	test
4	WOO	Jordan
5	Does this work yet?	test
6	Hello there.	test
7	Hello there.	test
8	Hello	test
9	Kimmy	test
10	5	Jordan
11	6	Jordan
12	7	Jordan
13	This is working now...almost	Jordan
14	Hello?	test
15	Hello there.	admin
16	Hello	test
17	Here we go!	Jordan
18	Admin	Jordan
19	HEY EVERYONE	Jordan
\.


--
-- Name: messages_msg_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('messages_msg_id_seq', 19, true);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY users (username, password, key_column) FROM stdin;
test	$2a$06$vsXjTBBhXz94FuyV2Q9pVuQbfMH/ZBUJXKU4etxLpqKStOf/r98D6	1
admin	$2a$06$.omTFl5.50RR7oXnt5qdtOTrYLYlLZH7mcGTRFrIrEkV6MCl4gZn2	2
tester	$2a$06$WJiLIfm8u420JRQ4cs6IguAr94PgiGK.Mjh0UMRh5PY1EEYYgRXQ.	3
mark	$2a$06$UAoZEJA.FFmLUeSM7/fe/effPUjA8vI1pHsWFnhuG6a7LSiw6FP8q	4
Tom	$2a$06$tmLfbfVZb.q7NbVdkVZryuQPXcuJI5ZoDUsrCYStaigHb8o59gSS2	5
Hella	$2a$06$OXqKt5wMPgof1T0CtjDMd.d0kaAbr62f9NgVJrgD4nQJ/dbU7i.Ye	6
Campbell	$2a$06$1YHFz7rOvYRU3xp/pzCuE.vrwFFk73SGWO1EtZ1S4uijsjmvV7a.2	8
Jordan	$2a$06$72I2MG3TyvBgJNeupYu0zOrfCjEn7wUw5EGTYMFXIe8B9m9LtXWtm	9
shaniqua	$2a$06$JIJfoKGckaS/5on3RbUVaeI.EfatEKm1qeFX1CkylAO0B8XFK3Rne	10
\.


--
-- Name: users_key_column_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('users_key_column_seq', 10, true);


--
-- Name: messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (msg_id);


--
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (key_column);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: messages; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE messages FROM PUBLIC;
REVOKE ALL ON TABLE messages FROM postgres;
GRANT ALL ON TABLE messages TO postgres;
GRANT SELECT,INSERT ON TABLE messages TO admin;


--
-- Name: messages_msg_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE messages_msg_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE messages_msg_id_seq FROM postgres;
GRANT ALL ON SEQUENCE messages_msg_id_seq TO postgres;
GRANT ALL ON SEQUENCE messages_msg_id_seq TO admin;


--
-- Name: users; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE users FROM PUBLIC;
REVOKE ALL ON TABLE users FROM postgres;
GRANT ALL ON TABLE users TO postgres;
GRANT ALL ON TABLE users TO admin;


--
-- Name: users_key_column_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE users_key_column_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE users_key_column_seq FROM postgres;
GRANT ALL ON SEQUENCE users_key_column_seq TO postgres;
GRANT ALL ON SEQUENCE users_key_column_seq TO admin;


--
-- PostgreSQL database dump complete
--

