"""
Git Operations Integration.

This module provides Git operations for project management:
- Clone, pull, push operations
- SSH key management
- Webhook support for auto-sync
- Branch and commit tracking

Example:
    >>> from agentic_assistants.integrations.git_ops import GitOperations
    >>> 
    >>> git = GitOperations()
    >>> 
    >>> # Clone a repository
    >>> git.clone("https://github.com/user/repo.git", "./project")
    >>> 
    >>> # Pull latest changes
    >>> git.pull("./project")
    >>> 
    >>> # Get repository status
    >>> status = git.get_status("./project")
"""

import os
import shutil
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class GitCredentials:
    """Git credentials configuration."""
    
    ssh_key_path: Optional[str] = None
    ssh_key_passphrase: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None  # For HTTPS with PAT
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding sensitive data)."""
        return {
            "has_ssh_key": self.ssh_key_path is not None,
            "has_username": self.username is not None,
            "has_token": self.token is not None,
        }


@dataclass
class CommitInfo:
    """Information about a Git commit."""
    
    sha: str
    short_sha: str
    message: str
    author_name: str
    author_email: str
    authored_date: datetime
    committer_name: str
    committer_email: str
    committed_date: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sha": self.sha,
            "short_sha": self.short_sha,
            "message": self.message,
            "author_name": self.author_name,
            "author_email": self.author_email,
            "authored_date": self.authored_date.isoformat(),
            "committer_name": self.committer_name,
            "committer_email": self.committer_email,
            "committed_date": self.committed_date.isoformat(),
        }


@dataclass
class BranchInfo:
    """Information about a Git branch."""
    
    name: str
    is_current: bool
    is_remote: bool
    tracking_branch: Optional[str] = None
    ahead: int = 0
    behind: int = 0
    last_commit: Optional[CommitInfo] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "is_current": self.is_current,
            "is_remote": self.is_remote,
            "tracking_branch": self.tracking_branch,
            "ahead": self.ahead,
            "behind": self.behind,
            "last_commit": self.last_commit.to_dict() if self.last_commit else None,
        }


@dataclass
class RepoStatus:
    """Git repository status."""
    
    branch: str
    is_clean: bool
    staged_files: List[str] = field(default_factory=list)
    modified_files: List[str] = field(default_factory=list)
    untracked_files: List[str] = field(default_factory=list)
    deleted_files: List[str] = field(default_factory=list)
    conflicted_files: List[str] = field(default_factory=list)
    ahead: int = 0
    behind: int = 0
    has_remote: bool = False
    remote_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "branch": self.branch,
            "is_clean": self.is_clean,
            "staged_files": self.staged_files,
            "modified_files": self.modified_files,
            "untracked_files": self.untracked_files,
            "deleted_files": self.deleted_files,
            "conflicted_files": self.conflicted_files,
            "ahead": self.ahead,
            "behind": self.behind,
            "has_remote": self.has_remote,
            "remote_url": self.remote_url,
        }


@dataclass
class GitOperationResult:
    """Result of a Git operation."""
    
    success: bool
    operation: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "operation": self.operation,
            "message": self.message,
            "details": self.details,
            "error": self.error,
        }


class GitOperations:
    """
    Git operations manager for project repositories.
    
    Provides:
    - Clone, pull, push, fetch operations
    - Branch management
    - Commit history
    - SSH key support
    - Status tracking
    """
    
    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        default_credentials: Optional[GitCredentials] = None,
    ):
        """
        Initialize Git operations manager.
        
        Args:
            config: Configuration instance
            default_credentials: Default credentials for Git operations
        """
        self.config = config or AgenticConfig()
        self.default_credentials = default_credentials
        self._repo_cache: Dict[str, Any] = {}
    
    def _get_repo(self, repo_path: str):
        """Get or create a Git repository object."""
        try:
            from git import Repo
        except ImportError:
            raise ImportError("gitpython not installed. Run: pip install gitpython")
        
        repo_path = str(Path(repo_path).resolve())
        
        if repo_path not in self._repo_cache:
            try:
                self._repo_cache[repo_path] = Repo(repo_path)
            except Exception:
                self._repo_cache[repo_path] = None
        
        return self._repo_cache[repo_path]
    
    def _setup_ssh_env(self, credentials: Optional[GitCredentials] = None) -> Dict[str, str]:
        """Setup SSH environment for Git operations."""
        credentials = credentials or self.default_credentials
        env = os.environ.copy()
        
        if credentials and credentials.ssh_key_path:
            key_path = Path(credentials.ssh_key_path).expanduser()
            if key_path.exists():
                # Create a temporary SSH command with the key
                ssh_cmd = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no'
                env['GIT_SSH_COMMAND'] = ssh_cmd
        
        return env
    
    def is_git_repo(self, path: str) -> bool:
        """
        Check if a path is a Git repository.
        
        Args:
            path: Path to check
            
        Returns:
            True if it's a Git repository
        """
        repo = self._get_repo(path)
        return repo is not None
    
    def clone(
        self,
        url: str,
        dest_path: str,
        branch: Optional[str] = None,
        credentials: Optional[GitCredentials] = None,
        depth: Optional[int] = None,
    ) -> GitOperationResult:
        """
        Clone a Git repository.
        
        Args:
            url: Repository URL
            dest_path: Destination path
            branch: Branch to clone (default: default branch)
            credentials: Git credentials
            depth: Clone depth (None for full clone)
            
        Returns:
            GitOperationResult
        """
        try:
            from git import Repo
        except ImportError:
            return GitOperationResult(
                success=False,
                operation="clone",
                message="gitpython not installed",
                error="pip install gitpython",
            )
        
        dest_path = str(Path(dest_path).resolve())
        
        # Check if destination exists
        if Path(dest_path).exists():
            return GitOperationResult(
                success=False,
                operation="clone",
                message=f"Destination path already exists: {dest_path}",
            )
        
        try:
            env = self._setup_ssh_env(credentials)
            
            clone_kwargs = {
                "url": url,
                "to_path": dest_path,
                "env": env,
            }
            
            if branch:
                clone_kwargs["branch"] = branch
            if depth:
                clone_kwargs["depth"] = depth
            
            repo = Repo.clone_from(**clone_kwargs)
            
            # Cache the repo
            self._repo_cache[dest_path] = repo
            
            return GitOperationResult(
                success=True,
                operation="clone",
                message=f"Cloned {url} to {dest_path}",
                details={
                    "url": url,
                    "path": dest_path,
                    "branch": branch or repo.active_branch.name,
                },
            )
            
        except Exception as e:
            return GitOperationResult(
                success=False,
                operation="clone",
                message=f"Clone failed: {str(e)}",
                error=str(e),
            )
    
    def pull(
        self,
        repo_path: str,
        remote: str = "origin",
        branch: Optional[str] = None,
        credentials: Optional[GitCredentials] = None,
    ) -> GitOperationResult:
        """
        Pull changes from remote.
        
        Args:
            repo_path: Repository path
            remote: Remote name
            branch: Branch to pull (default: current branch)
            credentials: Git credentials
            
        Returns:
            GitOperationResult
        """
        repo = self._get_repo(repo_path)
        if not repo:
            return GitOperationResult(
                success=False,
                operation="pull",
                message=f"Not a Git repository: {repo_path}",
            )
        
        try:
            env = self._setup_ssh_env(credentials)
            
            with repo.git.custom_environment(**env):
                # Fetch first
                repo.remotes[remote].fetch()
                
                # Pull
                if branch:
                    pull_info = repo.remotes[remote].pull(branch)
                else:
                    pull_info = repo.remotes[remote].pull()
            
            return GitOperationResult(
                success=True,
                operation="pull",
                message="Pull successful",
                details={
                    "remote": remote,
                    "branch": branch or repo.active_branch.name,
                    "commit": repo.head.commit.hexsha[:8],
                },
            )
            
        except Exception as e:
            return GitOperationResult(
                success=False,
                operation="pull",
                message=f"Pull failed: {str(e)}",
                error=str(e),
            )
    
    def push(
        self,
        repo_path: str,
        remote: str = "origin",
        branch: Optional[str] = None,
        force: bool = False,
        credentials: Optional[GitCredentials] = None,
    ) -> GitOperationResult:
        """
        Push changes to remote.
        
        Args:
            repo_path: Repository path
            remote: Remote name
            branch: Branch to push (default: current branch)
            force: Force push
            credentials: Git credentials
            
        Returns:
            GitOperationResult
        """
        repo = self._get_repo(repo_path)
        if not repo:
            return GitOperationResult(
                success=False,
                operation="push",
                message=f"Not a Git repository: {repo_path}",
            )
        
        try:
            env = self._setup_ssh_env(credentials)
            branch = branch or repo.active_branch.name
            
            with repo.git.custom_environment(**env):
                push_info = repo.remotes[remote].push(
                    branch,
                    force=force,
                )
            
            return GitOperationResult(
                success=True,
                operation="push",
                message="Push successful",
                details={
                    "remote": remote,
                    "branch": branch,
                    "commit": repo.head.commit.hexsha[:8],
                },
            )
            
        except Exception as e:
            return GitOperationResult(
                success=False,
                operation="push",
                message=f"Push failed: {str(e)}",
                error=str(e),
            )
    
    def fetch(
        self,
        repo_path: str,
        remote: str = "origin",
        credentials: Optional[GitCredentials] = None,
    ) -> GitOperationResult:
        """
        Fetch changes from remote without merging.
        
        Args:
            repo_path: Repository path
            remote: Remote name
            credentials: Git credentials
            
        Returns:
            GitOperationResult
        """
        repo = self._get_repo(repo_path)
        if not repo:
            return GitOperationResult(
                success=False,
                operation="fetch",
                message=f"Not a Git repository: {repo_path}",
            )
        
        try:
            env = self._setup_ssh_env(credentials)
            
            with repo.git.custom_environment(**env):
                fetch_info = repo.remotes[remote].fetch()
            
            return GitOperationResult(
                success=True,
                operation="fetch",
                message="Fetch successful",
                details={
                    "remote": remote,
                    "refs_updated": len(fetch_info),
                },
            )
            
        except Exception as e:
            return GitOperationResult(
                success=False,
                operation="fetch",
                message=f"Fetch failed: {str(e)}",
                error=str(e),
            )
    
    def get_status(self, repo_path: str) -> Optional[RepoStatus]:
        """
        Get repository status.
        
        Args:
            repo_path: Repository path
            
        Returns:
            RepoStatus or None if not a repo
        """
        repo = self._get_repo(repo_path)
        if not repo:
            return None
        
        try:
            # Get current branch
            branch = repo.active_branch.name
            
            # Check if clean
            is_clean = not repo.is_dirty(untracked_files=True)
            
            # Get file status
            staged = []
            modified = []
            untracked = []
            deleted = []
            conflicted = []
            
            # Staged files
            for item in repo.index.diff("HEAD"):
                staged.append(item.a_path)
            
            # Modified files
            for item in repo.index.diff(None):
                if item.deleted_file:
                    deleted.append(item.a_path)
                else:
                    modified.append(item.a_path)
            
            # Untracked files
            untracked = repo.untracked_files
            
            # Remote tracking
            has_remote = False
            remote_url = None
            ahead = 0
            behind = 0
            
            if repo.remotes:
                has_remote = True
                try:
                    remote_url = repo.remotes.origin.url
                except Exception:
                    pass
                
                # Check ahead/behind
                try:
                    tracking = repo.active_branch.tracking_branch()
                    if tracking:
                        commits_ahead = list(repo.iter_commits(f'{tracking.name}..HEAD'))
                        commits_behind = list(repo.iter_commits(f'HEAD..{tracking.name}'))
                        ahead = len(commits_ahead)
                        behind = len(commits_behind)
                except Exception:
                    pass
            
            return RepoStatus(
                branch=branch,
                is_clean=is_clean,
                staged_files=staged,
                modified_files=modified,
                untracked_files=untracked,
                deleted_files=deleted,
                conflicted_files=conflicted,
                ahead=ahead,
                behind=behind,
                has_remote=has_remote,
                remote_url=remote_url,
            )
            
        except Exception as e:
            logger.error(f"Failed to get status for {repo_path}: {e}")
            return None
    
    def get_branches(
        self,
        repo_path: str,
        include_remote: bool = True,
    ) -> List[BranchInfo]:
        """
        Get list of branches.
        
        Args:
            repo_path: Repository path
            include_remote: Include remote branches
            
        Returns:
            List of BranchInfo
        """
        repo = self._get_repo(repo_path)
        if not repo:
            return []
        
        branches = []
        current_branch = repo.active_branch.name
        
        # Local branches
        for branch in repo.heads:
            tracking = None
            ahead = 0
            behind = 0
            
            try:
                tracking_branch = branch.tracking_branch()
                if tracking_branch:
                    tracking = tracking_branch.name
                    commits_ahead = list(repo.iter_commits(f'{tracking}..{branch.name}'))
                    commits_behind = list(repo.iter_commits(f'{branch.name}..{tracking}'))
                    ahead = len(commits_ahead)
                    behind = len(commits_behind)
            except Exception:
                pass
            
            # Get last commit
            last_commit = None
            try:
                commit = branch.commit
                last_commit = self._commit_to_info(commit)
            except Exception:
                pass
            
            branches.append(BranchInfo(
                name=branch.name,
                is_current=(branch.name == current_branch),
                is_remote=False,
                tracking_branch=tracking,
                ahead=ahead,
                behind=behind,
                last_commit=last_commit,
            ))
        
        # Remote branches
        if include_remote and repo.remotes:
            for remote in repo.remotes:
                try:
                    for ref in remote.refs:
                        name = ref.name
                        if name.endswith('/HEAD'):
                            continue
                        
                        last_commit = None
                        try:
                            last_commit = self._commit_to_info(ref.commit)
                        except Exception:
                            pass
                        
                        branches.append(BranchInfo(
                            name=name,
                            is_current=False,
                            is_remote=True,
                            last_commit=last_commit,
                        ))
                except Exception:
                    pass
        
        return branches
    
    def get_commits(
        self,
        repo_path: str,
        branch: Optional[str] = None,
        limit: int = 50,
    ) -> List[CommitInfo]:
        """
        Get commit history.
        
        Args:
            repo_path: Repository path
            branch: Branch name (default: current branch)
            limit: Maximum commits to return
            
        Returns:
            List of CommitInfo
        """
        repo = self._get_repo(repo_path)
        if not repo:
            return []
        
        commits = []
        
        try:
            ref = branch or repo.active_branch.name
            for commit in repo.iter_commits(ref, max_count=limit):
                commits.append(self._commit_to_info(commit))
        except Exception as e:
            logger.error(f"Failed to get commits: {e}")
        
        return commits
    
    def _commit_to_info(self, commit) -> CommitInfo:
        """Convert a git commit to CommitInfo."""
        return CommitInfo(
            sha=commit.hexsha,
            short_sha=commit.hexsha[:8],
            message=commit.message.strip(),
            author_name=commit.author.name,
            author_email=commit.author.email,
            authored_date=datetime.fromtimestamp(commit.authored_date),
            committer_name=commit.committer.name,
            committer_email=commit.committer.email,
            committed_date=datetime.fromtimestamp(commit.committed_date),
        )
    
    def checkout(
        self,
        repo_path: str,
        branch: str,
        create: bool = False,
    ) -> GitOperationResult:
        """
        Checkout a branch.
        
        Args:
            repo_path: Repository path
            branch: Branch name
            create: Create branch if it doesn't exist
            
        Returns:
            GitOperationResult
        """
        repo = self._get_repo(repo_path)
        if not repo:
            return GitOperationResult(
                success=False,
                operation="checkout",
                message=f"Not a Git repository: {repo_path}",
            )
        
        try:
            if create:
                new_branch = repo.create_head(branch)
                new_branch.checkout()
            else:
                repo.heads[branch].checkout()
            
            return GitOperationResult(
                success=True,
                operation="checkout",
                message=f"Checked out branch: {branch}",
                details={"branch": branch, "created": create},
            )
            
        except Exception as e:
            return GitOperationResult(
                success=False,
                operation="checkout",
                message=f"Checkout failed: {str(e)}",
                error=str(e),
            )
    
    def commit(
        self,
        repo_path: str,
        message: str,
        add_all: bool = False,
        files: Optional[List[str]] = None,
    ) -> GitOperationResult:
        """
        Create a commit.
        
        Args:
            repo_path: Repository path
            message: Commit message
            add_all: Add all modified files
            files: Specific files to add
            
        Returns:
            GitOperationResult
        """
        repo = self._get_repo(repo_path)
        if not repo:
            return GitOperationResult(
                success=False,
                operation="commit",
                message=f"Not a Git repository: {repo_path}",
            )
        
        try:
            # Stage files
            if add_all:
                repo.git.add('-A')
            elif files:
                repo.index.add(files)
            
            # Commit
            commit = repo.index.commit(message)
            
            return GitOperationResult(
                success=True,
                operation="commit",
                message=f"Created commit: {commit.hexsha[:8]}",
                details={
                    "sha": commit.hexsha,
                    "message": message,
                },
            )
            
        except Exception as e:
            return GitOperationResult(
                success=False,
                operation="commit",
                message=f"Commit failed: {str(e)}",
                error=str(e),
            )
    
    def init(
        self,
        repo_path: str,
        initial_branch: str = "main",
    ) -> GitOperationResult:
        """
        Initialize a new Git repository.
        
        Args:
            repo_path: Repository path
            initial_branch: Initial branch name
            
        Returns:
            GitOperationResult
        """
        try:
            from git import Repo
        except ImportError:
            return GitOperationResult(
                success=False,
                operation="init",
                message="gitpython not installed",
                error="pip install gitpython",
            )
        
        repo_path = str(Path(repo_path).resolve())
        
        try:
            # Create directory if needed
            Path(repo_path).mkdir(parents=True, exist_ok=True)
            
            # Initialize repo
            repo = Repo.init(repo_path, initial_branch=initial_branch)
            
            # Cache it
            self._repo_cache[repo_path] = repo
            
            return GitOperationResult(
                success=True,
                operation="init",
                message=f"Initialized repository at {repo_path}",
                details={
                    "path": repo_path,
                    "branch": initial_branch,
                },
            )
            
        except Exception as e:
            return GitOperationResult(
                success=False,
                operation="init",
                message=f"Init failed: {str(e)}",
                error=str(e),
            )
    
    def add_remote(
        self,
        repo_path: str,
        name: str,
        url: str,
    ) -> GitOperationResult:
        """
        Add a remote to the repository.
        
        Args:
            repo_path: Repository path
            name: Remote name
            url: Remote URL
            
        Returns:
            GitOperationResult
        """
        repo = self._get_repo(repo_path)
        if not repo:
            return GitOperationResult(
                success=False,
                operation="add_remote",
                message=f"Not a Git repository: {repo_path}",
            )
        
        try:
            repo.create_remote(name, url)
            
            return GitOperationResult(
                success=True,
                operation="add_remote",
                message=f"Added remote: {name}",
                details={"name": name, "url": url},
            )
            
        except Exception as e:
            return GitOperationResult(
                success=False,
                operation="add_remote",
                message=f"Add remote failed: {str(e)}",
                error=str(e),
            )


class SSHKeyManager:
    """
    Manages SSH keys for Git operations.
    
    Provides:
    - Key generation
    - Key storage and retrieval
    - Key registration with services
    """
    
    def __init__(
        self,
        keys_directory: Optional[str] = None,
        config: Optional[AgenticConfig] = None,
    ):
        """
        Initialize SSH key manager.
        
        Args:
            keys_directory: Directory to store keys
            config: Configuration instance
        """
        self.config = config or AgenticConfig()
        
        if keys_directory:
            self.keys_dir = Path(keys_directory)
        else:
            self.keys_dir = Path(self.config.base_dir) / ".ssh_keys"
        
        self.keys_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_key(
        self,
        name: str,
        key_type: str = "ed25519",
        passphrase: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Generate a new SSH key pair.
        
        Args:
            name: Key name (used for file naming)
            key_type: Key type (ed25519, rsa)
            passphrase: Optional passphrase
            comment: Optional comment
            
        Returns:
            Tuple of (private_key_path, public_key_content)
        """
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
            from cryptography.hazmat.backends import default_backend
        except ImportError:
            raise ImportError("cryptography not installed. Run: pip install cryptography")
        
        private_key_path = self.keys_dir / f"{name}"
        public_key_path = self.keys_dir / f"{name}.pub"
        
        # Generate key pair
        if key_type == "ed25519":
            private_key = ed25519.Ed25519PrivateKey.generate()
        elif key_type == "rsa":
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
                backend=default_backend(),
            )
        else:
            raise ValueError(f"Unsupported key type: {key_type}")
        
        # Serialize private key
        if passphrase:
            encryption = serialization.BestAvailableEncryption(passphrase.encode())
        else:
            encryption = serialization.NoEncryption()
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.OpenSSH,
            encryption_algorithm=encryption,
        )
        
        # Serialize public key
        public_key = private_key.public_key()
        public_openssh = public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        )
        
        # Add comment to public key
        public_key_str = public_openssh.decode()
        if comment:
            public_key_str = f"{public_key_str} {comment}"
        
        # Save keys
        private_key_path.write_bytes(private_pem)
        private_key_path.chmod(0o600)
        
        public_key_path.write_text(public_key_str)
        
        logger.info(f"Generated SSH key: {private_key_path}")
        
        return str(private_key_path), public_key_str
    
    def list_keys(self) -> List[Dict[str, Any]]:
        """
        List all stored SSH keys.
        
        Returns:
            List of key info dictionaries
        """
        keys = []
        
        for key_file in self.keys_dir.iterdir():
            if key_file.suffix == ".pub":
                continue
            if key_file.is_file():
                public_file = key_file.with_suffix(key_file.suffix + ".pub")
                has_public = public_file.exists()
                
                keys.append({
                    "name": key_file.name,
                    "path": str(key_file),
                    "has_public_key": has_public,
                    "created": datetime.fromtimestamp(key_file.stat().st_ctime).isoformat(),
                })
        
        return keys
    
    def get_public_key(self, name: str) -> Optional[str]:
        """
        Get the public key content.
        
        Args:
            name: Key name
            
        Returns:
            Public key content or None
        """
        public_key_path = self.keys_dir / f"{name}.pub"
        
        if public_key_path.exists():
            return public_key_path.read_text()
        
        return None
    
    def delete_key(self, name: str) -> bool:
        """
        Delete an SSH key pair.
        
        Args:
            name: Key name
            
        Returns:
            True if deleted
        """
        private_key_path = self.keys_dir / name
        public_key_path = self.keys_dir / f"{name}.pub"
        
        deleted = False
        
        if private_key_path.exists():
            private_key_path.unlink()
            deleted = True
        
        if public_key_path.exists():
            public_key_path.unlink()
            deleted = True
        
        return deleted
