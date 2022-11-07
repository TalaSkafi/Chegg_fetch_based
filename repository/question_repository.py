from pymysql.converters import escape_string

from repository.Model.Question import Question


class QuestionRepository:

    def get_first_not_answer_retrived_k_questions(self, mysql_db_manager, process_id, number_of_questions):
        query = "SELECT id,chegg_id FROM question where (HW_has_answer_state='NOT_CHECKED')    " \
                "and process_id='" + str(process_id) + "' " + " limit " + str(number_of_questions)
        result = mysql_db_manager.excute_query_fetchall(query)
        if not result:
            return None
        questions = []
        for row in result:
            questions.append(Question(row[0], row[1],""))
        return questions

    def get_top_k_not_crawled_HW_URL(self, mysql_db_manager, process_ids, number_of_questions):
        query = "SELECT id,chegg_id,HW_answer_URL FROM question where HW_has_answer_state='HAS_ANSWER' and HW_answer_URL is not null and HW_answer_crawled=0   " \
                "and process_id in (" + str(process_ids) + ") " + " limit " + str(number_of_questions)
        print(query)
        result = mysql_db_manager.excute_query_fetchall(query)
        if not result:
            return None
        questions = []
        for row in result:
            questions.append(Question(row[0], row[1],row[2]))
        return questions

    def update_HW_has_answer_state(self,mysql_db_manager,question_id,answer_state):
        query = "UPDATE question SET HW_has_answer_state = '" + answer_state + "' where id="+str(question_id)
        mysql_db_manager.excute_query(query)

    def update_generated_url_answer  (self,mysql_db_manager,question_id,HW_answer_URL,):
        query = "UPDATE question SET" +" HW_has_answer_state ='HAS_ANSWER',HW_answer_URL = '" + HW_answer_URL + "'  where id=" + str(question_id)
        mysql_db_manager.excute_query(query)


    def update_question_by_answer_html(self, mysql_db_manager, question_id, answer_HTML,):
        query = "UPDATE question SET answer_html = '" + escape_string(str(answer_HTML)) + "',HW_answer_crawled=1 where id=" + str(question_id)
        mysql_db_manager.excute_query(query)

    def get_crawled_count(self,mysql_db_manager):
        query = "SELECT COUNT(*) FROM question where HW_answer_crawled=1  "
        result = mysql_db_manager.excute_query_fetchall(query)
        return result[0][0]

    def get_produced_count(self, mysql_db_manager):
        query = "SELECT COUNT(*) FROM question where HW_has_answer_state='HAS_ANSWER' and HW_answer_URL is not null and HW_answer_crawled=0"
        result = mysql_db_manager.excute_query_fetchall(query)
        return result[0][0]
