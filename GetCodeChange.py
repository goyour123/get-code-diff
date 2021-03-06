import os
import json
import shutil
import git

def dir_creator(dir_path):
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)

def dir_tree_creator(src, dst):
    src_item = src.split('/')
    dst_target = dst
    if len(src_item) > 1:
        for index, item in enumerate(src_item):
            dst = dst + '/' + item
            if index < len(src_item) - 1:
                if not os.path.isdir(dst):
                    os.mkdir(dst)
            if index == len(src_item) - 2:
                dst_target = dst
    return dst_target

def config_init():
    with open('config.json') as cfgJson:
        config = json.load(cfgJson)

    return config['dest_path'], config['source_path'], config['sha'], config['branch']

def main():

    dst_path, repo_path, commit_sha, branch = config_init()

    dst_mod_path, dst_org_path = dst_path + '/Modified', dst_path + '/Original'
    for dirt in [dst_mod_path, dst_org_path]:
        dir_creator(dirt)

    repo = git.Repo(repo_path)
    repo_git = repo.git

    commit = repo.commit(commit_sha)
    pre_commit = commit.parents[0]

    print('Comparing diff files')
    diffs = commit.diff(pre_commit)

    org_branch = repo.active_branch.name

    print('Checking out to ' + commit_sha)
    repo_git.checkout(commit)

    tree_files = []
    for f in diffs:
        dst_path_target = dir_tree_creator(f.a_blob.path, dst_mod_path)
        tree_files.append(f.a_blob.path)
        src_path = repo_path + '/' + f.a_blob.path
        if os.path.isfile(src_path):
            print('Copying ' + src_path + ' to ' + dst_path_target)
            shutil.copy(src_path, dst_path_target)

    print('Checking out to previous commit')
    repo_git.checkout(pre_commit)

    for f in tree_files:
        dst_path_target = dir_tree_creator(f, dst_org_path)
        src_path = repo_path + '/' + f
        if os.path.isfile(src_path):
            print('Copying ' + src_path + ' to ' + dst_path_target)
            shutil.copy(src_path, dst_path_target)

    repo_git.checkout(org_branch)

if __name__ == '__main__':
    main()