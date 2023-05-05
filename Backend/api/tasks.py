from .models import TasksModel, NotificationsModel


def send_notification(task):
    title = "Срок, отведенный на выполнение задачи истек"
    for user in task.users.all():
        description = f"""Уважаемый(ая) {user.username},
    
    Хотели бы сообщить вам, что срок, отведенный на выполнение задачи '{task.title}', истек. В настоящий момент задача не 
    выполнена в установленные сроки.
    
    Пожалуйста, примите меры для выполнения задачи незамедлительно, чтобы избежать задержек и проблем. Если у вас 
    возникли какие-либо проблемы или причины, по которым вы не смогли завершить задачу вовремя, пожалуйста, свяжитесь с 
    вашим руководителем или ответственным лицом, чтобы обсудить дальнейшие шаги.
    
    С уважением,
    администрация TaskManager"""

        NotificationsModel.objects.create(title=title, description=description, _from='System', user=user)

