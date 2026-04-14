
create database smart_learning 
CREATE SCHEMA IF NOT EXISTS vs
-----------------------------------master table-----------------------------------

create table  vs.study_plan(
study_plan_id int generated always as identity primary key,
universities varchar(100) not null,
stream varchar(100) not null,
departments varchar(100) not null,
subjects varchar(100), 
sem int not null,
module_no int not null,
model_description varchar(100),
topics varchar(200)
)
select *from vs.study_plan
insert into vs.study_plan (universities, stream, departments, subjects, sem, module_no, model_description, topics)
values('pondicherry university', 'b.tech', 'electronics and communication engineering',
'engineering mathematics – I', 1, 1, 'linear algebra', 'rank of a matrix'), 

('pondicherry university', 'b.tech', 'electronics and communication engineering',
'engineering mathematics – I', 1, 1, 'linear algebra', 'consistency of a system of linear equations'), 

('pondicherry university', 'b.tech', 'electronics and communication engineering',
'engineering mathematics – I', 1, 1, 'linear algebra', 'Eigenvalues and Eigenvectors'), 

('pondicherry university', 'b.tech', 'electronics and communication engineering',
'Chemistry', 1, 1, 'atomic and molecular structure', 'Molecular orbitals of diatomic molecules'), 

('pondicherry university', 'b.tech', 'electronics and communication engineering',
'Chemistry', 1, 1, 'atomic and molecular structure', 'band theory of solids'), 

('pondicherry university', 'b.tech', 'electronics and communication engineering',
'Chemistry', 1, 1, 'atomic and molecular structure', 'Liquid crystal and its applications');

------------------------------------user info------------------------------------

create table vs.user_basic_info(
student_id int generated always as identity primary key,
student_name varchar(100) not null,
university varchar(100) not null,
college_name varchar(100) not null,
stream varchar(100) not null,
std_year int not null,
department varchar(100) not null, 
sem int not null,
mobile_no varchar(15) unique not null,
email_id varchar(100) unique not null,
telegram_id varchar(50) unique not null
)

------------------------------------Study_activity---------------------------------

create table vs.student_activity(
id_no int generated always as identity primary key,
student_id int not null, 
study_plan_id int not null, 
is_done BOOLEAN NOT NULL DEFAULT FALSE,
mark int default 0,
    constraint fk_student
        foreign key (student_id)
        references vs.user_basic_info(student_id)
        on delete cascade,

    constraint fk_plan
        foreign key (study_plan_id)
        references vs.study_plan(study_plan_id)
        on delete cascade,

    constraint unique_student_task
        unique (student_id, study_plan_id)
)

SELECT current_database();