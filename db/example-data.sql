/**********************************************************************************
 * _author  : Domeniko Gentner
 * _mail    : code@tuxstash.de
 * _repo    : https://git.tuxstash.de/gothseidank/labertasche
 * _license : This project is under MIT License
 **********************************************************************************
 *
 * This script generates sample data for the example implementation.
 * Feed it into the automatically created database with either DBBeaver
 * or the sqlite command line tool. 
 * 
 * Please note: Labertasche must have run once to create the database!
 * 
 **********************************************************************************
 */

/* delete old data */
DELETE FROM t_comments;
DELETE FROM t_projects;
DELETE FROM t_email;
DELETE FROM t_comments;
DELETE FROM t_location;

/* Create example projects */
INSERT INTO t_projects (id_project, name) 
	VALUES 
		(1, 'default'),
		(2, 'example.com'),
		(3, 'tuxstash.de'),
		(4, 'beispiel.de'),
		(5, 'labertasche.tuxstash.de')
;		

/* Create existing locations for each project */
INSERT INTO t_location (id_location, location, project_id) 
	VALUES
		(1, '/blog/stramine/', 1),
		(2, '/blog/readme/', 1),
		(3, '/blog/article-1/', 2),
		(4, '/blog/article-2/', 2),
		(5, '/blog/article-3/', 3),
		(6, '/blog/article-4/', 3),
		(7, '/blog/article-5/', 4),
		(8, '/blog/article-6/', 4),
		(9, '/blog/article-7/', 5),
		(10, '/blog/article-8/', 5)
;
		
/* Create some emails that are blocked and allowed */
INSERT INTO t_email (id_email, email, is_allowed, is_blocked, project_id)
	VALUES
		(1, "commenter1@example.com", true, false, 1),
		(2, "commenter2@example.com", false, true, 1),
		(3, "commenter3@example.com", true, false, 2),
		(4, "commenter4@example.com", false, true, 2),
		(5, "commenter5@example.com", true, false, 3),
		(6, "commenter6@example.com", false, true, 3),
		(7, "commenter7@example.com", true, false, 4),
		(8, "commenter8@example.com", false, true, 4),
		(9, "commenter9@example.com", true, false, 5),
		(10, "commenter10@example.com", false, true, 5)
;

		
/* Create some comments */
INSERT INTO t_comments (comments_id, location_id, email, content, created_on, is_published, is_spam, spam_score, replied_to, confirmation, deletion, gravatar, project_id)
	VALUES
		(1, 1, 'commenter1@example.com', '1 This is a test comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', true, false, 0.99, NULL, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 1),
		(2, 1, 'commenter2@example.com', '2 This is a reply to the previous comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', true, false, 0.99, 1, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 1),
		(3, 2, 'commenter3@example.com', '3 This is a test comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', true, false, 0.99, NULL, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 1),
		(4, 2, 'commenter4@example.com', '4 This is a reply to the previous comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', true, false, 0.99, 3, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 1),
		
		(5, 3, 'commenter5@example.com', '5 This is a test comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', true, false, 0.99, NULL, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 2),
		(6, 3, 'commenter6@example.com', '6 This is a reply to the previous comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', true, false, 0.99, 5, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 2),
		(7, 4, 'commenter7@example.com', '7 This is a test comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', true, false, 0.99, NULL, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 2),
		(8, 4, 'commenter8@example.com', '8 This is a reply to the previous comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', true, false, 0.99, 7, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 2),
		
		(9, 5, 'commenter9@example.com', '9 This is a test comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', false, true, 0.09, NULL, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 3),
		(10, 5, 'commenter10@example.com', '10 This is a reply to the previous comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', true, false, 0.99, 9, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 3),
		(11, 6, 'commenter11@example.com', '11 This is a test comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', true, false, 0.09, NULL, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 3),
		(12, 6, 'commenter12@example.com', '12 This is a reply to the previous comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', true, false, 0.99, 11, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 3),
		
		(13, 7, 'commenter13@example.com', '13 This is a test comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', true, false, 0.99, NULL, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 4),
		(14, 7, 'commenter14@example.com', '14 This is a reply to the previous comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', true, false, 0.99, 13, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 4),
		(15, 8, 'commenter15@example.com', '15 This is a test comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', true, false, 0.99, NULL, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 4),
		(16, 8, 'commenter16@example.com', '16 This is a reply to the previous comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', true, false, 0.99, 16, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 4),
		
		(17, 9, 'commenter17@example.com', '17 This is a test comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', true, false, 0.99, NULL, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 5),
		(18, 9, 'commenter18@example.com', '18 This is a reply to the previous comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', true, false, 0.99, 18, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 5),	
		(19, 10, 'commenter19@example.com', '19 This is a test comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', true, false, 0.99, NULL, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 5),
		(20, 10, 'commenter20@example.com', '20 This is a reply to the previous comment and has no actual value. Please test all methods on this.', '2020-12-16  23:37:00.000000', true, false, 0.99, 19, NULL, NULL, 'd9eef4df0ae5bfc1a9a9b1e39a99c07f', 5)
;
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
	