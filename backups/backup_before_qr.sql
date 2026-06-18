--
-- PostgreSQL database dump
--

\restrict 6IpCjnQboNEKOmyDfo0DzyWg84ycAyRM6BzhNtFOdSzYc8wuWDDWanlUFxUQsWC

-- Dumped from database version 16.14 (Debian 16.14-1.pgdg13+1)
-- Dumped by pg_dump version 16.14 (Debian 16.14-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: cafes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cafes (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    code character varying(100) NOT NULL,
    address character varying(255),
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.cafes OWNER TO postgres;

--
-- Name: cafes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cafes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cafes_id_seq OWNER TO postgres;

--
-- Name: cafes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cafes_id_seq OWNED BY public.cafes.id;


--
-- Name: surveys; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.surveys (
    id integer NOT NULL,
    cafe_id integer NOT NULL,
    created_by_user_id integer NOT NULL,
    visit_datetime timestamp without time zone NOT NULL,
    table_number integer NOT NULL,
    q1 boolean NOT NULL,
    q2 boolean NOT NULL,
    q3 boolean NOT NULL,
    q4 boolean NOT NULL,
    comment_text text,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.surveys OWNER TO postgres;

--
-- Name: surveys_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.surveys_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.surveys_id_seq OWNER TO postgres;

--
-- Name: surveys_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.surveys_id_seq OWNED BY public.surveys.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    telegram_id bigint NOT NULL,
    full_name character varying(255) NOT NULL,
    role character varying(50) NOT NULL,
    cafe_id integer,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: cafes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cafes ALTER COLUMN id SET DEFAULT nextval('public.cafes_id_seq'::regclass);


--
-- Name: surveys id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.surveys ALTER COLUMN id SET DEFAULT nextval('public.surveys_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
47a0d5023e73
\.


--
-- Data for Name: cafes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cafes (id, name, code, address, is_active, created_at) FROM stdin;
1	АндерСон Таганская 36	cafe_taganskaya_36	-	t	2026-05-31 13:19:25.010961
2	АндерСон Авеню	cafe_avenyu	-	t	2026-05-31 13:19:25.019076
3	АндерСон Братиславская	cafe_bratislavskaya	-	t	2026-05-31 13:19:25.024625
4	АндерСон Бутово	cafe_butovo	-	t	2026-05-31 13:19:25.028833
5	АндерСон Гагаринский	cafe_gagarinskiy	-	t	2026-05-31 13:19:25.032762
6	АндерСон Гиляровского	cafe_gilyarovskogo	-	t	2026-05-31 13:19:25.036879
7	АндерСон Домодедово	cafe_domodedovo	-	t	2026-05-31 13:19:25.041243
8	АндерСон Кусковская	cafe_kuskovskaya	-	t	2026-05-31 13:19:25.044542
9	АндерСон Каскад	cafe_kaskad	-	t	2026-05-31 13:19:25.047864
10	АндерСон Медведково	cafe_medvedkovo	-	t	2026-05-31 13:19:25.050993
11	АндерСон Мичуринский	cafe_michurinskiy	-	t	2026-05-31 13:19:25.054326
12	АндерСон Обручева	cafe_obrucheva	-	t	2026-05-31 13:19:25.057654
13	АндерСон Островитянова	cafe_ostrovityanova	-	t	2026-05-31 13:19:25.061495
14	АндерСон Сокол	cafe_sokol	-	t	2026-05-31 13:19:25.065435
15	АндерСон Царицыно	cafe_tsaritsyno	-	t	2026-05-31 13:19:25.069335
\.


--
-- Data for Name: surveys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.surveys (id, cafe_id, created_by_user_id, visit_datetime, table_number, q1, q2, q3, q4, comment_text, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, telegram_id, full_name, role, cafe_id, is_active, created_at) FROM stdin;
1	752571022	nikita_superuser	superuser	\N	t	2026-05-31 13:20:43.018913
\.


--
-- Name: cafes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cafes_id_seq', 15, true);


--
-- Name: surveys_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.surveys_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: cafes cafes_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cafes
    ADD CONSTRAINT cafes_code_key UNIQUE (code);


--
-- Name: cafes cafes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cafes
    ADD CONSTRAINT cafes_pkey PRIMARY KEY (id);


--
-- Name: surveys surveys_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.surveys
    ADD CONSTRAINT surveys_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_telegram_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_telegram_id_key UNIQUE (telegram_id);


--
-- Name: surveys surveys_cafe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.surveys
    ADD CONSTRAINT surveys_cafe_id_fkey FOREIGN KEY (cafe_id) REFERENCES public.cafes(id);


--
-- Name: surveys surveys_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.surveys
    ADD CONSTRAINT surveys_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id);


--
-- Name: users users_cafe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_cafe_id_fkey FOREIGN KEY (cafe_id) REFERENCES public.cafes(id);


--
-- PostgreSQL database dump complete
--

\unrestrict 6IpCjnQboNEKOmyDfo0DzyWg84ycAyRM6BzhNtFOdSzYc8wuWDDWanlUFxUQsWC

