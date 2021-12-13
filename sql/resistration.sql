CREATE TABLE public.resistration(
	user_id INTEGER NOT NULL,
	area_id INTEGER NOT NULL,
	FOREIGN KEY (user_id) REFERENCES public.user(id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (area_id) REFERENCES public.area(id) ON DELETE CASCADE ON UPDATE CASCADE
);