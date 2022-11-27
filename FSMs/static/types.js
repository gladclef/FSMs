function is_str(val)
{
    return (typeof val == "string");
}

function is_jquery(obj) {
    return obj instanceof jQuery;
}

function is_dom(obj) {
    // https://stackoverflow.com/questions/28287499/jquery-check-if-variable-is-dom-element
    function checkInstance(elem) {
        if ((elem instanceof jQuery && elem.length) || elem instanceof HTMLElement) {
            return true;
        }
        return false;
    }

    if (obj instanceof HTMLCollection && obj.length) {
        for(var a = 0, len = obj.length; a < len; a++) {
            if(!checkInstance(obj[a])) {
                // console.log(a);
                return false;
            }
        }
        return true;
    } else {
        return checkInstance(obj);
    }
}