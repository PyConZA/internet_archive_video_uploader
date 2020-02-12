""" Archive.org video uploader. """

import sys
import os
import optparse

import yaml

import internetarchive as ia


class Config(object):
    """ Video upload configuration holder. """

    def __init__(self, config_file):
        with open(config_file) as config_stream:
            config = yaml.safe_load(config_stream)
        self._config = config

    @property
    def folder(self):
        return self._config['folder']

    @property
    def default_metadata(self):
        return self._config['default_metadata']

    @property
    def videos(self):
        return [
            Video(self, **v)
            for v in self._config['videos']
        ]


class Video(object):
    """ Information about a video to be uploaded. """

    def __init__(self, config, filename, identifier=None, metadata=None, **kw):
        self._config = config
        self.identifier = identifier
        self.filename = filename
        self._metadata = metadata or {}
        self._extra = kw

    def __repr__(self):
        return "<Video path=%r>" % (self.path,)

    def __getattr__(self, name):
        return self._extra.get(name)

    @property
    def path(self):
        return os.path.join(self._config.folder, self.filename)

    @property
    def metadata(self):
        md = self._config.default_metadata.copy()
        md.update(self._metadata)
        return md


def upload_video(v, **kw):
    """ Upload a video. """

    print "Uploading %s ... [%s]" % (v.path, v.identifier)
    print ""
    print "  Metadata"
    print "  --------"
    md = v.metadata
    for key in sorted(md.keys()):
        print "  %r: %r" % (key, md[key])

    item = ia.get_item(v.identifier)
    item.upload(v.path, metadata=md, **kw)


def ia_access_tokens():
    """ Retrieve access token from environment. """
    token = os.getenv("IAS3_TOKEN")
    if token is None:
        raise RuntimeError(
            "Please set 'export IAS3_TOKEN=\"<access-token>:<secret-key>\"'.")
    return token.split(":")


def main(args):
    """ Run an upload. """
    parser = optparse.OptionParser()
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                      default=False, help="Be more verbose during uploads")
    options, args = parser.parse_args(args)

    conf = Config("videos.yaml")
    access_key, secret_key = ia_access_tokens()
    for v in conf.videos:
        if not v.upload:
            continue
        upload_video(v, access_key=access_key, secret_key=secret_key,
                     verbose=options.verbose)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
