def valid_int(f):
    return f is not None and isinstance(f, int) and f > 0,


def valid_string(f):
    return f is not None and isinstance(f, str) and len(f) > 0


def valid_movement(f):
    return valid_string(f) and f != 'All'


def inflate_payload(fields, values):
    return {field: values[field]
            for field, valid in fields.items()
            if valid(values[field])}


field_validation = {
    'search': valid_string
}
field_conversion = {
    
}


def get_post_param(request, field):
    if field_validation.get(field, lambda x: False)(request.POST.get(field)):
        return field_conversion.get(field, lambda x: x)(request.POST.get(field))
    return None
