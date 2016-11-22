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
        requests.post(url, data=data.URL)

    def get_playlist(self, data):
        url = self.host + '/playlist'
        r = requests.get(url)
        playlist = json.loads(r.text)
        if 'title' not in playlist['first_song'].keys():
            playlist['first_song']['title'] = 'Nothing :-('
        print("Currently Playing:\n\n    {}".format(
            playlist['first_song']['title'])
        )
        print("\nNext:\n")
        for i in playlist['playlist']:
            print("    {}  {}".format(i['score'], i['title']))

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

    def __init__(self):
        self.client_session = ClientSession()
        parser = argparse.ArgumentParser(
            description="Client for yt-jukebox"
        )
        subparsers = parser.add_subparsers(
            title='Supported commands', dest='command')
        subparsers.required = True

        self.add_new_parser(subparsers, name='submit',
                            help='Submit a song',
                            arg_help='URL of the song',
                            arg='URL', func=self.client_session.submit)

        self.add_new_parser(subparsers, name='playlist',
                            help='Get the current playlist',
                            func=self.client_session.get_playlist)

        self.add_new_parser(subparsers, name='next',
                            help='Play next song (admin)',
                            func=self.client_session.play_next_song)

        self.add_new_parser(subparsers, name='play',
                            help='Restart paused song (admin)',
                            func=self.client_session.play)

        self.add_new_parser(subparsers, name='pause',
                            help='Pause music (admin)',
                            func=self.client_session.pause)

        self.add_new_parser(subparsers, name='upvote',
                            help='Upvote a song',
                            arg_help='Name of the song',
                            arg='SONG', func=self.client_session.upvote)

        self.add_new_parser(subparsers, name='downvote',
                            help='Downvote a song',
                            arg_help='Name of the song',
                            arg='SONG', func=self.client_session.downvote)

        self.add_new_parser(subparsers, name='delete',
                            help='Delete a song (admin)',
                            arg_help='Name of the song',
                            arg='SONG', func=self.client_session.delete)

        args = parser.parse_args(argv[1:])
        args.func(args)


def main():
    my_shell = Shell()
