import json
import sys
import optparse

LOG_ENTRY_SET = set()

def readlog(l):
    f = open(l)
    for line in iter(f):
        prefix_mark = line.find('{')
        json_string = line[prefix_mark:]
        try:
            json_obj = json.loads(json_string)
        except ValueError:
            continue;
        json_enc = json.JSONEncoder().encode(json_string)

        if json_enc not in LOG_ENTRY_SET:
            LOG_ENTRY_SET.add(json_enc)


def print_matching(keypath, value):
    print_count = 0
    for j in LOG_ENTRY_SET:
        decoded = json.JSONDecoder().decode(j)
        decoded_json = json.loads(decoded)

        # -s key=value
        if keypath and value:
            mvalue = value_for_key_path(keypath, decoded_json)
            if mvalue is None or mvalue != value:
                continue

        # -a
        elif not keypath and not value:
            pass

        # pretty print json
        print print_count, json.dumps(decoded_json, sort_keys=True, indent=3,\
             separators=(',', ': '))
        print_count += 1


def print_unique(keypath):
    uset = set()
    for j in LOG_ENTRY_SET:
        decoded = json.JSONDecoder().decode(j)
        decoded_json = json.loads(decoded)
        value = value_for_key_path(keypath, decoded_json)
        if value not in uset:
            uset.add(value)
    for i,j in enumerate(uset):
        print "%-4s%s" % (i, j)


def value_for_key_path(key, dicto):
    skeys = key.split('.')
    try:
        t = dicto[skeys[0]]
        for i in range(1, len(skeys)):
            t = t[skeys[i]]
        return t
    except KeyError:
        return None


if __name__ == "__main__":
    # setup command line option parser
    parser = optparse.OptionParser(usage="usage: %prog [options] filename",
                    version="%prog 0.1")
    parser.add_option("-s", "--search",
                    dest="search_kv",
                    metavar='k=v',
                    help="search for key=value pair")
    parser.add_option("-a", "--all",
                    dest="search_all",
                    action="store_true",
                    default=False,
                    help="print all entries")
    parser.add_option("-u", "--unique",
                    dest="search_uk",
                    metavar='key',
                    help="print all unique keys with value")

    (options, args) = parser.parse_args()

    # do some error checking
    if options.search_kv and options.search_uk and options.search_all:
        parser.error("options -s, -u, and -a are mutually exclusive")
    if len(args) != 1:
        parser.error("wrong number of arguments")

    # read in log file
    readlog(args[0])

    # print all entries
    if options.search_all == True:
        print_matching(None, None)
        pass
    # searching for key=value pair
    elif options.search_kv:
        kvp = options.search_kv.split('=')
        print_matching(kvp[0], kvp[1])
    # print unique keys
    else:
        print_unique(options.search_uk)
