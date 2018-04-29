import logging
import time

logger = logging.getLogger(__name__)


def limit_job_speed(max_job_speed, job_step=1):
    speed_stat = {
        'start_time': time.time(),
        'job_num': 0,
        'tick_time': 5,
    }

    def _limit(job_args):
        try:
            max_speed = max_job_speed
            if callable(max_job_speed):
                max_speed = max_job_speed()

            speed_stat['job_num'] += job_step

            min_ts = speed_stat['job_num'] * 1.0 / max_speed
            itv_ts = time.time() - speed_stat['start_time']
            if itv_ts < min_ts:
                time.sleep(min_ts - itv_ts)

            now = time.time()
            if now - speed_stat['start_time'] >= speed_stat['tick_time']:
                speed = speed_stat['job_num'] * 1.0 / (now - speed_stat['start_time'])

                logger.info('current speed: {speed}/s max_speed:{max_speed}/s'
                            ' job_num:{job_num} start_time:{start_time}'.format(
                                speed=round(speed, 3),
                                max_speed=max_speed,
                                job_num=speed_stat['job_num'],
                                start_time=speed_stat['start_time']))

                speed_stat['start_time'] = now
                speed_stat['job_num'] = 0

        except Exception as e:
            logger.exception('error occurred limit job speed: ' + repr(e))

        return job_args

    return _limit
