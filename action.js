const core = require('@actions/core');
const exec = require('@actions/exec');

async function run() {
	try {
		if (process.platform === 'win32') throw 'Do not run this action on a Windows VM'

		var target = 'master'
		if (process.env.GITHUB_BASE_REF) {
			target = process.env.GITHUB_BASE_REF;
		}

		var stdout;
		var stderr;

		const options = function () {
			stdout = [];
			stderr = [];
			const options = {};
			options.listeners = {};
			options.listeners.stdout = (data) => { stdout = data.toString().split('\n'); stdout.pop(); };
			options.listeners.stderr = (data) => { stderr = data.toString().split('\n'); stderr.pop(); };
			options.silent = true;
			options.ignoreReturnCode = true;

			return options;
		}

		await exec.exec('git rev-parse --abbrev-ref HEAD', [], options());
		await exec.exec('git branch ' + stdout[0] + ' --contains origin/' + target, [], options());
		if (stdout.length !== 1) {
			core.error('This commit is not on top of ' + target);
			core.error('(no further validation is done due to this error)');
			throw '';
		}

		console.log('Branch is on top of ' + target);

		process.env.HOOKS_DIR = './hooks';
		process.env.GIT_DIR = '.git';
		if (await exec.exec('./hooks/check-commits.sh origin/' + target + '..HEAD', [], options())) {
			stderr.forEach(core.error);
			throw '';
		}
		console.log('Commit checks passed');
	} catch (error) {
		core.setFailed(error);
	}
}

run();
