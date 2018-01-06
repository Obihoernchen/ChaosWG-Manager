/* global $ */
function process_btn_press(element, state) {
    var popover = element.parents('.popover');
    var taskid = popover.prev().data('taskid');
    var data = {id: taskid, state: state};
    // send actual HTTP POST request to app
    // TODO: this is bad but whatever...
    $.post('/set_task_state', data, location.reload());
    // TODO error handling
    //popover.popover('hide');
    // TODO improve
    //location.reload();
}

// ready not needed because it's loaded at the end of body
//$(document).ready(function(){
    // Init popovers
    var popovers = $('[data-toggle="popover"]');
    popovers.popover({
        placement: 'bottom',
        html: true,
        content: '<div class="btn-group">' +
                 '<button type="button" class="btn btn-warning btn-backlog">Backlog</button>' +
                 '<button type="button" class="btn btn-danger btn-todo">ToDo</button>' +
                 '<button type="button" class="btn btn-success btn-done">Done</button>' +
                 '</div>'
    });
    // Only one popover at a time
    popovers.click(function(){
        popovers.not(this).popover('hide');
    });
    // Button events
    $(document).on('click', '.popover .close', function(){
        $(this).parents('.popover').popover('hide');
    });
    $(document).on('click', '.btn-backlog', function(){
        process_btn_press($(this), 0);
    });
    $(document).on('click', '.btn-todo', function(){
        process_btn_press($(this), 1);
    });
    $(document).on('click', '.btn-done', function(){
        process_btn_press($(this), 2);
    });
//});
