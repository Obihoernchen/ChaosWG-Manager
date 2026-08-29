/* global bootstrap */
// Bootstrap 5 (jQuery-free) rewrite of the old tasks.js.

const { Popover } = bootstrap;

const BTN_GROUP_HTML =
    '<div class="btn-group" role="group" aria-label="Set task state">' +
    '<button type="button" class="btn btn-warning btn-backlog">Backlog</button>' +
    '<button type="button" class="btn btn-danger btn-todo">ToDo</button>' +
    '<button type="button" class="btn btn-success btn-done">Done</button>' +
    '</div>';

// One Popover instance per task row
const popovers = new Map(); // trigger element -> Popover instance
let openTrigger = null; // trigger whose popover is open (only one at a time)

document.querySelectorAll('[data-bs-toggle="popover"]').forEach(el => {
    const inst = new Popover(el, {
        placement: 'bottom auto',
        html: true,
        trigger: 'click',
        content: BTN_GROUP_HTML
    });
    popovers.set(el, inst);

    // Only one popover at a time: hide the others when one opens
    el.addEventListener('show.bs.popover', () => {
        popovers.forEach((other, trigger) => {
            if (trigger !== el) other.hide();
        });
    });
    el.addEventListener('shown.bs.popover', () => {
        openTrigger = el;
    });
});

function setTaskState(taskid, state) {
    // send actual HTTP POST request to app
    fetch('/set_task_state', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: new URLSearchParams({id: String(taskid), state: String(state)})
    }).then(() => {
        // Reload page after new state was set
        // TODO reloading the whole page is bad but whatever...
        location.reload();
    });
    // TODO error handling?
}

document.addEventListener('click', e => {
    const stateButtons = {'.btn-backlog': 0, '.btn-todo': 1, '.btn-done': 2};
    for (const [selector, state] of Object.entries(stateButtons)) {
        if (e.target.closest(selector)) {
            setTaskState(openTrigger.dataset.taskid, state);
            return;
        }
    }
    // close button inside the popover title
    if (e.target.closest('.popover .btn-close')) {
        popovers.get(openTrigger).hide();
    }
});
