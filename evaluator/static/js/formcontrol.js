class FormControl {
    constructor(query) {
        this.count = 0;
        this.el = Array.from(document.body.querySelectorAll(query))
    }
    getNext() {
        if (this.count + 1 < this.el.length) {
            return this.el[this.count + 1]
        }
        else {
            return undefined;
        }
    }
    setNext() {
        if (this.count + 1 < this.el.length) {
            this.count++;
            return this.el[this.count];
        }
        else
            return undefined;
    }
    getPrev() {
        if (this.count - 1 >= 0) {
            return this.el[this.count - 1];
        }
        else {
            return undefined;
        }
    }
    setPrev() {
        if (this.count - 1 >= 0) {
            this.count--;
            return this.el[this.count];
        }
        else {
            return undefined
        }
    }
}

var fieldsets = new FormControl("fieldset");

var next_btn = document.body.querySelector(".next_btn");
var prev_btn = document.body.querySelector(".prev_btn");

function changeAttr(el, name, value, replace=false, replace_val) {
    console.log(el);
    if (typeof el == "string") {
        el = document.body.querySelector(el);
    }
    var el_attr = el.getAttribute(name);
    if (replace) {
        el.setAttribute(name, el_attr.replace(value, replace_val).trim());
    }
    else {
        el.setAttribute(name, el_attr.concat(` ${value}`));
    }
}
function functoryNext(e) {
    var next = fieldsets.setNext();
    var prev = fieldsets.getPrev();
    if (next) {
        changeAttr(next, "class", "hidden", true, "");
        changeAttr(".next_btn", "class", "not_visible", true, "");
        if (!fieldsets.getNext()) {
            changeAttr(".next_btn", "class", "not_visible");
        }
    }
    else {
        changeAttr(".next_btn", "class", "not_visible");
    }

    if (prev) {
        changeAttr(prev, "class", "hidden");
        changeAttr(".prev_btn", "class", "not_visible", true, "");
    }
    else {
        changeAttr(".prev_btn", "class", "not_visible");
    }
}
function functoryPrev(e) {
    var prev = fieldsets.setPrev();
    var next = fieldsets.getNext();
    if (prev) {
        changeAttr(prev, "class", "hidden", true, "");
        changeAttr(".prev_btn", "class", "not_visible", true, "");
        if (!fieldsets.getPrev()) {
            changeAttr(".prev_btn", "class", "not_visible");
        }
    }
    else {
        changeAttr(".prev_btn", "class", "not_visible");
    }

    if (next) {
        changeAttr(next, "class", "hidden");
        changeAttr(".next_btn", "class", "not_visible", true, "");
    }
    else {
        changeAttr(".prev_btn", "class", "not_visible");
    }
}
next_btn.addEventListener("click", functoryNext);
prev_btn.addEventListener("click", functoryPrev);