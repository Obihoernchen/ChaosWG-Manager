/* global bootstrap */
// Bootstrap 5 (jQuery-free) rewrite of the old tasks.js.

const { Popover } = bootstrap;

const BTN_GROUP_HTML =
    '<div class="btn-group" role="group" aria-label="Set task state">' +
    '<button type="button" class="btn btn-warning btn-backlog">Backlog</button>' +
    '<button type="button" class="btn btn-danger btn-todo">ToDo</button>' +
    '<button type="button" class="btn btn-success btn-done">Done</button>' +
    '</div>';

// Bootstrap 5 sanitizes html:true popover content and removes every element
// whose tag is not in the allow-list (Bootstrap 5.3: js/src/util/sanitizer.js).
// The built-in DefaultAllowlist has no `button`, so all three state buttons
// were silently stripped -> the popover opened, but was empty.
// This is a copy of Bootstrap's DefaultAllowlist with `button` added.
const ALLOW_LIST = {
    '*': ['class', 'dir', 'id', 'lang', 'role', /^aria-[\w-]*$/i],
    a: ['target', 'href', 'title', 'rel'],
    area: [], b: [], br: [], col: [], code: [], dd: [], div: [], dl: [], dt: [],
    em: [], hr: [], h1: [], h2: [], h3: [], h4: [], h5: [], h6: [], i: [],
    img: ['src', 'srcset', 'alt', 'title', 'width', 'height'],
    li: [], ol: [], p: [], pre: [], s: [], small: [], span: [], sub: [], sup: [],
    strong: [], u: [], ul: [],
    button: []
};

// One Popover instance per task row
const popovers = new Map(); // trigger element -> Popover instance
let openTrigger = null; // trigger whose popover is open (only one at a time)

document.querySelectorAll('[data-bs-toggle="popover"]').forEach(el => {
    const inst = new Popover(el, {
        // Popper v2 (Bootstrap 5) only accepts 'top'|'right'|'bottom'|'left' plus
        // optional '-start'/'-end'. The old Bootstrap 4 string 'bottom auto' made
        // popper's offset modifier read data['bottom auto'] -> undefined and throw
        // "Cannot read properties of undefined (reading 'x')", leaving the popover
        // unpositioned (empty popup in the corner). 'bottom' + popper's flip
        // modifier gives the same "bottom, flip if no space" behaviour.
        placement: 'bottom',
        html: true,
        trigger: 'click',
        content: BTN_GROUP_HTML,
        allowList: ALLOW_LIST
    });
    popovers.set(el, inst);

    // Only one popover at a time: hide the others when one opens.
    // openTrigger is set as soon as the popover *starts* showing (not after
    // the fade-in) so that a fast click on a state button inside the
    // still-animating popover can already resolve its task id instead of
    // crashing on a null openTrigger.
    el.addEventListener('show.bs.popover', () => {
        openTrigger = el;
        popovers.forEach((other, trigger) => {
            if (trigger !== el) other.hide();
        });
    });
    el.addEventListener('hidden.bs.popover', () => {
        // a superseded popover finishing its fade-out must not clear the
        // trigger of the popover that replaced it
        if (openTrigger === el) openTrigger = null;
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
    if (!openTrigger) return;
    // close button inside the popover title
    if (e.target.closest('.popover .btn-close')) {
        popovers.get(openTrigger).hide();
        return;
    }
    // Bootstrap 5 popovers with trigger: 'click' do not close on outside
    // clicks, so do it manually. Clicks inside the open popover (e.g. the
    // state buttons) and on the trigger itself are ignored: the trigger
    // already toggles the popover, and the state buttons need the popover
    // to stay open while the request is sent.
    const openPopover = document.querySelector('.popover.show');
    if (openPopover
        && !openPopover.contains(e.target)
        && !openTrigger.contains(e.target)) {
        popovers.get(openTrigger).hide();
    }
});
