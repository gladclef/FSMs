def post(url, args):
    return "(vals, on_success, on_failure) => { return post(\""+url+"\", vals, on_success, on_failure); }(args);"