#!/usr/bin/python3

import os
from sys import argv

import json
import requests
import argparse


class MissingAuth(Exception):
    pass


class ClientSession(object):
    def __init__(self, host="127.0.0.1", port=9090, prefix="http://"):
        self.host = prefix + host + ':' + str(port)

    def submit(self, data):
        url = self.host + '/playlist'
        request_data = {
            'url': data.URL,
            'tags': (data.tag or [])
        }
        requests.post(url, data=json.dumps(request_data))

    def get_playlist(self, data):
        url = self.host + '/playlist'
        r = requests.get(url)
        playlist = json.loads(r.text)
        print('\nTheme: {}\n'.format(playlist['theme']))
        if 'title' not in playlist['first_song'].keys():
            playlist['first_song']['title'] = 'Nothing :-('
        print(u"Currently Playing:\n\n    {}".format(
            playlist['first_song']['title'])
        )
        print("\nNext:\n")
        for i in playlist['playlist']:
            print(u"    {}  {}".format(i['score'], i['title']))

    def upvote(self, data):
        url = self.host + '/vote/up/' + data.SONG
        requests.post(url, data=data.SONG)

    def downvote(self, data):
        url = self.host + '/vote/down/' + data.SONG
        requests.post(url, data=data.SONG)

    @staticmethod
    def get_identity():
        user = os.environ.get('JUKEBOX_ADMIN_USER')
        password = os.environ.get('JUKEBOX_ADMIN_PASSWORD')
        if not user or not password:
            raise MissingAuth('You must define the JUKEBOX_ADMIN_PASSWORD'
                              'And the JUKEBOX_ADMIN_USER'
                              'environment variables')
        return (user, password)

    def play_next_song(self, data):
        url = self.host + '/admin/next'
        requests.post(url, auth=self.get_identity())

    def pause(self, data):
        url = self.host + '/admin/pause'
        requests.post(url, auth=self.get_identity())

    def play(self, data):
        url = self.host + '/admin/play'
        requests.post(url, auth=self.get_identity())

    def delete(self, data):
        url = self.host + '/admin/delete'
        requests.delete(url, auth=self.get_identity(), data=data.SONG)

    def set_theme(self, data):
        url = self.host + '/admin/theme'
        requests.post(url, auth=self.get_identity(), data=data.THEME)

    def add_tags(self, data):
        url = self.host + '/admin/add_tags'
        req_data = json.dumps(data.tag or [])
        requests.post(url, auth=self.get_identity(), data=req_data)

    def remove_tags(self, data):
        url = self.host + '/admin/remove_tags'
        req_data = json.dumps(data.tag or [])
        requests.post(url, auth=self.get_identity(), data=req_data)


class Shell(object):
    @staticmethod
    def add_new_parser(subparsers,
                       name=None, help=None, arg=None,
                       arg_help=None, func=None):
        new_parser = subparsers.add_parser(
            name=name,
            help=help)
        if arg:
            new_parser.add_argument(arg,
                                    help=arg_help,
                                    type=str)
        new_parser.set_defaults(func=func)
        return new_parser

    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Client for yt-jukebox"
        )
        parser.add_argument(
            '--host',
            required=False,
            default='127.0.0.1',
            help='Host of the kingjuke server (defaults to 127.0.0.1)'
        )
        parser.add_argument(
            '--port',
            required=False,
            default=9090,
            type=int,
            help='Port on which the kingjuke server'
            ' is listening (defaults to 9090)'
        )
        subparsers = parser.add_subparsers(
            title='Supported commands', dest='command')
        subparsers.required = True
        submit_parser = self.add_new_parser(subparsers, name='submit',
                                            help='Submit a song',
                                            arg_help='URL of the song',
                                            arg='URL', func='submit')
        submit_parser.add_argument('-t', '--tag', action='append')

        self.add_new_parser(subparsers, name='playlist',
                            help='Get the current playlist',
                            func='get_playlist')

        self.add_new_parser(subparsers, name='next',
                            help='Play next song (admin)',
                            func='play_next_song')

        self.add_new_parser(subparsers, name='play',
                            help='Restart paused song (admin)',
                            func='play')

        self.add_new_parser(subparsers, name='pause',
                            help='Pause music (admin)',
                            func='pause')

        self.add_new_parser(subparsers, name='upvote',
                            help='Upvote a song',
                            arg_help='Name of the song',
                            arg='SONG', func='upvote')

        self.add_new_parser(subparsers, name='downvote',
                            help='Downvote a song',
                            arg_help='Name of the song',
                            arg='SONG', func='downvote')

        self.add_new_parser(subparsers, name='delete',
                            help='Delete a song (admin)',
                            arg_help='Name of the song',
                            arg='SONG', func='delete')

        self.add_new_parser(subparsers, name='theme',
                            help='Set the playlist theme (admin)',
                            arg_help='theme',
                            arg='THEME', func='set_theme')

        tag_parser = self.add_new_parser(subparsers, name='add-tag',
                                         help='Authorize a tag (admin)',
                                         func='add_tags')
        tag_parser.add_argument('-t', '--tag', action='append', required=True)

        tag_parser = self.add_new_parser(subparsers, name='remove-tag',
                                         help='Forbid a tag (admin)',
                                         func='remove_tags')
        tag_parser.add_argument('-t', '--tag', action='append', required=True)

        args = parser.parse_args(argv[1:])
        self.client_session = ClientSession(host=args.host, port=args.port)
        func = getattr(self.client_session, args.func)
        func(args)


def main():
    my_shell = Shell()
