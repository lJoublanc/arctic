from pandas import DataFrame, MultiIndex, Index, Series
from datetime import datetime as dt
from pandas.util.testing import assert_frame_equal, assert_series_equal
from arctic.date import DateRange
from arctic.exceptions import NoDataFoundException
import pandas as pd
import numpy as np
import random
import pytest
import pymongo

from arctic.chunkstore.chunkstore import START, SYMBOL
from arctic.chunkstore.passthrough_chunker import PassthroughChunker


def test_write_dataframe(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3]},
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 1),
                                                 (dt(2016, 1, 2), 1),
                                                 (dt(2016, 1, 3), 1)],
                                                names=['date', 'id'])
                   )
    chunkstore_lib.write('test_df', df, chunk_size='D')
    read_df = chunkstore_lib.read('test_df')
    assert_frame_equal(df, read_df)


def test_upsert_dataframe(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3]},
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 1),
                                                 (dt(2016, 1, 2), 1),
                                                 (dt(2016, 1, 3), 1)],
                                                names=['date', 'id'])
                   )
    chunkstore_lib.update('test_df', df, upsert=True)
    read_df = chunkstore_lib.read('test_df')
    assert_frame_equal(df, read_df)


def test_write_dataframe_noindex(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3],
                         'date': [dt(2016, 1, 1),
                                  dt(2016, 1, 2),
                                  dt(2016, 1, 3)]
                         }
                   )
    chunkstore_lib.write('test_df', df)
    read_df = chunkstore_lib.read('test_df')
    assert_frame_equal(df, read_df)


def test_overwrite_dataframe(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3, 4]},
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 1),
                                                 (dt(2016, 1, 2), 1),
                                                 (dt(2016, 1, 3), 1),
                                                 (dt(2016, 1, 4), 1)],
                                                names=['date', 'id'])
                   )

    dg = DataFrame(data={'data': [1, 2, 3]},
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 1),
                                                 (dt(2016, 1, 2), 1),
                                                 (dt(2016, 1, 3), 1)],
                                                names=['date', 'id'])
                   )
    chunkstore_lib.write('test_df', df)
    chunkstore_lib.write('test_df', dg)
    read_df = chunkstore_lib.read('test_df')
    assert_frame_equal(dg, read_df)


def test_overwrite_dataframe_noindex(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3, 4],
                         'date': [dt(2016, 1, 1),
                                  dt(2016, 1, 2),
                                  dt(2016, 1, 3),
                                  dt(2016, 1, 4)]})

    df2 = DataFrame(data={'data': [5, 6, 7, 8],
                          'date': [dt(2016, 1, 1),
                                   dt(2016, 1, 2),
                                   dt(2016, 1, 3),
                                   dt(2016, 1, 4)]})

    chunkstore_lib.write('test_df', df)
    chunkstore_lib.write('test_df', df2)
    read_df = chunkstore_lib.read('test_df')
    assert_frame_equal(df2, read_df)


def test_overwrite_dataframe_monthly(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3, 4, 5, 6]},
                   index=MultiIndex.from_tuples([(dt(2016, 1, 5), 1),
                                                 (dt(2016, 2, 5), 1),
                                                 (dt(2016, 3, 5), 1),
                                                 (dt(2016, 4, 5), 1),
                                                 (dt(2016, 5, 5), 1),
                                                 (dt(2016, 6, 5), 1)],
                                                names=['date', 'id'])
                   )

    dg = DataFrame(data={'data': [1, 2, 3, 4, 5, 6]},
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 1),
                                                 (dt(2016, 2, 2), 1),
                                                 (dt(2016, 3, 3), 1),
                                                 (dt(2016, 4, 4), 1),
                                                 (dt(2016, 5, 5), 1),
                                                 (dt(2016, 6, 6), 1)],
                                                names=['date', 'id'])
                   )
    chunkstore_lib.write('test_df', df, chunk_size='M')
    chunkstore_lib.write('test_df', dg, chunk_size='M')
    read_df = chunkstore_lib.read('test_df')
    assert_frame_equal(dg, read_df)


def test_write_read_with_daterange(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3]},
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 1),
                                                 (dt(2016, 1, 2), 1),
                                                 (dt(2016, 1, 3), 1)],
                                                names=['date', 'id'])
                   )

    dg = DataFrame(data={'data': [1, 2]},
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 1),
                                                 (dt(2016, 1, 2), 1)],
                                                names=['date', 'id'])
                   )

    chunkstore_lib.write('test_df', df)
    read_df = chunkstore_lib.read('test_df', chunk_range=DateRange(dt(2016, 1, 1), dt(2016, 1, 2)))

    assert_frame_equal(read_df, dg)
    read_with_dr = chunkstore_lib.read('test_df', chunk_range=pd.date_range(dt(2016, 1, 1), dt(2016, 1, 2)))
    assert_frame_equal(read_df, dg)


def test_write_read_with_daterange_noindex(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3],
                         'date': [dt(2016, 1, 1),
                                  dt(2016, 1, 2),
                                  dt(2016, 1, 3)]})

    dg = DataFrame(data={'data': [1, 2],
                         'date': [dt(2016, 1, 1),
                                  dt(2016, 1, 2)]})

    chunkstore_lib.write('test_df', df)
    read_df = chunkstore_lib.read('test_df', chunk_range=DateRange(dt(2016, 1, 1), dt(2016, 1, 2)))
    assert_frame_equal(read_df, dg)

def test_store_single_index_df(chunkstore_lib):
    df = DataFrame(data=[1, 2, 3],
                   index=Index(data=[dt(2016, 1, 1),
                                     dt(2016, 1, 2),
                                     dt(2016, 1, 3)],
                               name='date'),
                   columns=['data'])

    chunkstore_lib.write('chunkstore_test', df, chunk_size='D')
    ret = chunkstore_lib.read('chunkstore_test', chunk_range=DateRange(dt(2016, 1, 1), dt(2016, 1, 3)))
    assert_frame_equal(df, ret)


def test_no_range(chunkstore_lib):
    df = DataFrame(data=[1, 2, 3],
                   index=Index(data=[dt(2016, 1, 1),
                                     dt(2016, 1, 2),
                                     dt(2016, 1, 3)],
                               name='date'),
                   columns=['data'])

    chunkstore_lib.write('chunkstore_test', df, chunk_size='D')
    ret = chunkstore_lib.read('chunkstore_test')
    assert_frame_equal(df, ret)


def test_closed_open(chunkstore_lib):
    df = DataFrame(data=[1, 2, 3],
                   index=Index(data=[dt(2016, 1, 1),
                                     dt(2016, 1, 2),
                                     dt(2016, 1, 3)],
                               name='date'),
                   columns=['data'])

    chunkstore_lib.write('chunkstore_test', df, chunk_size='D')
    ret = chunkstore_lib.read('chunkstore_test', chunk_range=DateRange(dt(2016, 1, 1), None))
    assert_frame_equal(df, ret)


def test_open_closed(chunkstore_lib):
    df = DataFrame(data=[1, 2, 3],
                   index=Index(data=[dt(2016, 1, 1),
                                     dt(2016, 1, 2),
                                     dt(2016, 1, 3)],
                               name='date'),
                   columns=['data'])

    chunkstore_lib.write('chunkstore_test', df, chunk_size='D')
    ret = chunkstore_lib.read('chunkstore_test', chunk_range=DateRange(None, dt(2017, 1, 1)))
    assert_frame_equal(df, ret)


def test_monthly_df(chunkstore_lib):
    df = DataFrame(data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                   index=Index(data=[dt(2016, 1, 1),
                                     dt(2016, 1, 2),
                                     dt(2016, 1, 3),
                                     dt(2016, 1, 4),
                                     dt(2016, 1, 5),
                                     dt(2016, 2, 1),
                                     dt(2016, 2, 2),
                                     dt(2016, 2, 3),
                                     dt(2016, 2, 4),
                                     dt(2016, 3, 1)],
                               name='date'),
                   columns=['data'])

    chunkstore_lib.write('chunkstore_test', df, chunk_size='M')
    ret = chunkstore_lib.read('chunkstore_test', chunk_range=DateRange(dt(2016, 1, 1), dt(2016, 1, 2)))
    assert len(ret) == 2
    assert_frame_equal(df, chunkstore_lib.read('chunkstore_test'))


def test_yearly_df(chunkstore_lib):
    df = DataFrame(data=[1, 2, 3],
                   index=Index(data=[dt(2016, 1, 1),
                                     dt(2016, 2, 1),
                                     dt(2016, 3, 3)],
                               name='date'),
                   columns=['data'])

    chunkstore_lib.write('chunkstore_test', df, chunk_size='Y')
    ret = chunkstore_lib.read('chunkstore_test', chunk_range=DateRange(dt(2016, 1, 1), dt(2016, 3, 3)))
    assert_frame_equal(df, ret)


def test_append_daily(chunkstore_lib):
    df = DataFrame(data=[1, 2, 3],
                   index=Index(data=[dt(2016, 1, 1),
                                     dt(2016, 1, 2),
                                     dt(2016, 1, 3)],
                               name='date'),
                   columns=['data'])

    chunkstore_lib.write('chunkstore_test', df, chunk_size='D')
    df2 = DataFrame(data=[4, 5, 6],
                    index=Index(data=[dt(2016, 1, 4),
                                      dt(2016, 1, 5),
                                      dt(2016, 1, 6)],
                                name='date'),
                    columns=['data'])
    chunkstore_lib.append('chunkstore_test', df2)
    ret = chunkstore_lib.read('chunkstore_test', chunk_range=DateRange(dt(2016, 1, 1), dt(2016, 1, 6)))
    assert_frame_equal(ret, pd.concat([df, df2]))


def test_append_monthly(chunkstore_lib):
    df = DataFrame(data=[1, 2, 3],
                   index=Index(data=[dt(2016, 1, 1),
                                     dt(2016, 2, 1),
                                     dt(2016, 3, 1)],
                               name='date'),
                   columns=['data'])

    chunkstore_lib.write('chunkstore_test', df, chunk_size='M')
    df2 = DataFrame(data=[4, 5, 6],
                    index=Index(data=[dt(2016, 4, 1),
                                      dt(2016, 5, 1),
                                      dt(2016, 6, 1)],
                                name='date'),
                    columns=['data'])
    chunkstore_lib.append('chunkstore_test', df2)
    ret = chunkstore_lib.read('chunkstore_test', chunk_range=DateRange(dt(2016, 1, 1), dt(2016, 12, 31)))
    assert_frame_equal(ret, pd.concat([df, df2]))


def test_append_yearly(chunkstore_lib):
    df = DataFrame(data=[1, 2, 3],
                   index=Index(data=[dt(2010, 1, 1),
                                     dt(2011, 1, 1),
                                     dt(2012, 1, 1)],
                               name='date'),
                   columns=['data'])

    chunkstore_lib.write('chunkstore_test', df, chunk_size='Y')
    df2 = DataFrame(data=[4, 5, 6],
                    index=Index(data=[dt(2013, 1, 1),
                                      dt(2014, 1, 1),
                                      dt(2015, 1, 1)],
                                name='date'),
                    columns=['data'])
    chunkstore_lib.append('chunkstore_test', df2)
    ret = chunkstore_lib.read('chunkstore_test', chunk_range=DateRange(dt(2000, 1, 1), dt(2100, 12, 31)))
    assert_frame_equal(ret, pd.concat([df, df2]))


def test_append_existing_chunk(chunkstore_lib):
    df = DataFrame(data=[1.7, 2.8, 3.1],
                   index=Index(data=[dt(2016, 1, 1),
                                     dt(2016, 1, 2),
                                     dt(2016, 1, 3)],
                               name='date'),
                   columns=['data'])

    chunkstore_lib.write('chunkstore_test', df, chunk_size='M')
    df2 = DataFrame(data=[4.0, 5.1, 6.9],
                    index=Index(data=[dt(2016, 1, 4),
                                      dt(2016, 1, 5),
                                      dt(2016, 1, 6)],
                                name='date'),
                    columns=['data'])
    chunkstore_lib.append('chunkstore_test', df2)
    ret = chunkstore_lib.read('chunkstore_test', chunk_range=DateRange(dt(2016, 1, 1), dt(2016, 1, 31)))
    assert_frame_equal(ret, pd.concat([df, df2]))


def test_store_objects_df(chunkstore_lib):
    df = DataFrame(data=['1', '2', '3'],
                   index=Index(data=[dt(2016, 1, 1),
                                     dt(2016, 1, 2),
                                     dt(2016, 1, 3)],
                               name='date'),
                   columns=['data'])

    chunkstore_lib.write('chunkstore_test', df, chunk_size='D')
    ret = chunkstore_lib.read('chunkstore_test', chunk_range=DateRange(dt(2016, 1, 1), dt(2016, 1, 3)))
    assert_frame_equal(df, ret)


def test_empty_range(chunkstore_lib):
    df = DataFrame(data={'data': [1], 'values': [10]},
                   index=Index(data=[dt(2016, 1, 1)], name='date'))
    chunkstore_lib.write('chunkstore_test', df, chunk_size='D')
    df = chunkstore_lib.read('chunkstore_test', chunk_range=DateRange(dt(2016, 1, 2)))
    assert(df.empty)


def test_update(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3]},
                   index=pd.Index(data=[dt(2016, 1, 1),
                                        dt(2016, 1, 2),
                                        dt(2016, 1, 3)], name='date'))
    df2 = DataFrame(data={'data': [20, 30, 40]},
                    index=pd.Index(data=[dt(2016, 1, 2),
                                         dt(2016, 1, 3),
                                         dt(2016, 1, 4)], name='date'))

    equals = DataFrame(data={'data': [1, 20, 30, 40]},
                       index=pd.Index(data=[dt(2016, 1, 1),
                                            dt(2016, 1, 2),
                                            dt(2016, 1, 3),
                                            dt(2016, 1, 4)], name='date'))

    chunkstore_lib.write('chunkstore_test', df, chunk_size='D')
    chunkstore_lib.update('chunkstore_test', df2)
    assert_frame_equal(chunkstore_lib.read('chunkstore_test'), equals)
    assert(chunkstore_lib.get_info('chunkstore_test')['len'] == len(equals))
    assert(chunkstore_lib.get_info('chunkstore_test')['chunk_count'] == len(equals))


def test_update_no_overlap(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3]},
                   index=pd.Index(data=[dt(2016, 1, 1),
                                        dt(2016, 1, 2),
                                        dt(2016, 1, 3)], name='date'))
    df2 = DataFrame(data={'data': [20, 30, 40]},
                    index=pd.Index(data=[dt(2015, 1, 2),
                                         dt(2015, 1, 3),
                                         dt(2015, 1, 4)], name='date'))

    equals = DataFrame(data={'data': [20, 30, 40, 1, 2, 3]},
                       index=pd.Index(data=[dt(2015, 1, 2),
                                            dt(2015, 1, 3),
                                            dt(2015, 1, 4),
                                            dt(2016, 1, 1),
                                            dt(2016, 1, 2),
                                            dt(2016, 1, 3)], name='date'))

    chunkstore_lib.write('chunkstore_test', df, chunk_size='D')
    chunkstore_lib.update('chunkstore_test', df2)
    assert_frame_equal(chunkstore_lib.read('chunkstore_test'), equals)


def test_update_chunk_range(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3]},
                   index=pd.Index(data=[dt(2015, 1, 1),
                                        dt(2015, 1, 2),
                                        dt(2015, 1, 3)], name='date'))
    df2 = DataFrame(data={'data': [30]},
                    index=pd.Index(data=[dt(2015, 1, 2)],
                                   name='date'))
    equals = DataFrame(data={'data': [30, 3]},
                       index=pd.Index(data=[dt(2015, 1, 2),
                                            dt(2015, 1, 3)],
                                      name='date'))

    chunkstore_lib.write('chunkstore_test', df, chunk_size='M')
    chunkstore_lib.update('chunkstore_test', df2, chunk_range=DateRange(dt(2015, 1, 1), dt(2015, 1, 2)))
    assert_frame_equal(chunkstore_lib.read('chunkstore_test'), equals)


def test_update_chunk_range_overlap(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3]},
                   index=pd.Index(data=[dt(2015, 1, 1),
                                        dt(2015, 1, 2),
                                        dt(2015, 1, 3)], name='date'))

    chunkstore_lib.write('chunkstore_test', df, chunk_size='M')
    chunkstore_lib.update('chunkstore_test', df, chunk_range=DateRange(dt(2015, 1, 1), dt(2015, 1, 3)))
    assert_frame_equal(chunkstore_lib.read('chunkstore_test'), df)


def test_append_before(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3]},
                   index=pd.Index(data=[dt(2016, 1, 1),
                                        dt(2016, 1, 2),
                                        dt(2016, 1, 3)], name='date'))
    df2 = DataFrame(data={'data': [20, 30, 40]},
                    index=pd.Index(data=[dt(2015, 1, 2),
                                         dt(2015, 1, 3),
                                         dt(2015, 1, 4)], name='date'))

    equals = DataFrame(data={'data': [20, 30, 40, 1, 2, 3]},
                       index=pd.Index(data=[dt(2015, 1, 2),
                                            dt(2015, 1, 3),
                                            dt(2015, 1, 4),
                                            dt(2016, 1, 1),
                                            dt(2016, 1, 2),
                                            dt(2016, 1, 3)], name='date'))

    chunkstore_lib.write('chunkstore_test', df, chunk_size='D')
    chunkstore_lib.append('chunkstore_test', df2)
    assert_frame_equal(chunkstore_lib.read('chunkstore_test') , equals)


def test_append_and_update(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3]},
                   index=pd.Index(data=[dt(2016, 1, 1),
                                        dt(2016, 1, 2),
                                        dt(2016, 1, 3)], name='date'))
    df2 = DataFrame(data={'data': [20, 30, 40]},
                    index=pd.Index(data=[dt(2015, 1, 2),
                                         dt(2015, 1, 3),
                                         dt(2015, 1, 4)], name='date'))

    df3 = DataFrame(data={'data': [100, 300]},
                    index=pd.Index(data=[dt(2015, 1, 2),
                                         dt(2016, 1, 2)], name='date'))

    equals = DataFrame(data={'data': [100, 30, 40, 1, 300, 3]},
                       index=pd.Index(data=[dt(2015, 1, 2),
                                            dt(2015, 1, 3),
                                            dt(2015, 1, 4),
                                            dt(2016, 1, 1),
                                            dt(2016, 1, 2),
                                            dt(2016, 1, 3)], name='date'))

    chunkstore_lib.write('chunkstore_test', df, chunk_size='D')
    chunkstore_lib.append('chunkstore_test', df2)
    chunkstore_lib.update('chunkstore_test', df3)
    assert_frame_equal(chunkstore_lib.read('chunkstore_test') , equals)


def test_update_same_df(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3]},
                   index=pd.Index(data=[dt(2016, 1, 1),
                                        dt(2016, 1, 2),
                                        dt(2016, 1, 3)], name='date'))
    chunkstore_lib.write('chunkstore_test', df, chunk_size='D')

    sym = chunkstore_lib._get_symbol_info('chunkstore_test')
    chunkstore_lib.update('chunkstore_test', df)
    assert(sym == chunkstore_lib._get_symbol_info('chunkstore_test'))


def test_df_with_multiindex(chunkstore_lib):
    df = DataFrame(data=[1, 2, 3],
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 2),
                                                 (dt(2016, 1, 2), 3),
                                                 (dt(2016, 1, 3), 2)],
                                                names=['date', 'security']))
    chunkstore_lib.write('pandas', df, chunk_size='D')
    saved_df = chunkstore_lib.read('pandas')
    assert np.all(df.values == saved_df.values)


def test_with_strings(chunkstore_lib):
    df = DataFrame(data={'data': ['A', 'B', 'C']},
                   index=pd.Index(data=[dt(2016, 1, 1),
                                        dt(2016, 1, 2),
                                        dt(2016, 1, 3)], name='date'))
    chunkstore_lib.write('chunkstore_test', df, chunk_size='D')
    read_df = chunkstore_lib.read('chunkstore_test')
    assert_frame_equal(read_df, df)


def test_with_strings_multiindex_append(chunkstore_lib):
    df = DataFrame(data={'data': ['A', 'BBB', 'CC']},
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 2),
                                                 (dt(2016, 1, 1), 3),
                                                 (dt(2016, 1, 2), 2)],
                                                names=['date', 'security']))
    chunkstore_lib.write('chunkstore_test', df, chunk_size='D')
    read_df = chunkstore_lib.read('chunkstore_test')
    assert_frame_equal(read_df, df)
    df2 = DataFrame(data={'data': ['AAAAAAA']},
                    index=MultiIndex.from_tuples([(dt(2016, 1, 2), 4)],
                                                 names=['date', 'security']))
    chunkstore_lib.append('chunkstore_test', df2)
    df = DataFrame(data={'data': ['A', 'BBB', 'CC', 'AAAAAAA']},
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 2),
                                                 (dt(2016, 1, 1), 3),
                                                 (dt(2016, 1, 2), 2),
                                                 (dt(2016, 1, 2), 4)],
                                                names=['date', 'security']))
    assert_frame_equal(chunkstore_lib.read('chunkstore_test') , df)


def gen_daily_data(month, days, securities):
    for day in days:
        openp = [round(random.uniform(50.0, 100.0), 1) for x in securities]
        closep = [round(x + random.uniform(-5.0, 5.0), 1) for x in openp]

        index_list = [(dt(2016, month, day), s) for s in securities]
        yield DataFrame(data={'open': openp, 'close': closep},
                        index=MultiIndex.from_tuples(index_list,
                                                     names=['date', 'security']))


def write_random_data(chunkstore_lib, name, month, days, securities, chunk_size='D', update=False, append=False):
    '''
    will generate daily data and write it in daily chunks
    regardless of what the chunk_size is set to.
    month: integer
    days: list of integers
    securities: list of integers
    chunk_size: one of 'D', 'M', 'Y'
    update: force update for each daily write
    append: force append for each daily write
    '''
    df_list = []
    for df in gen_daily_data(month, days, securities):
        if update:
            chunkstore_lib.update(name, df)
        elif append or len(df_list) > 0:
            chunkstore_lib.append(name, df)
        else:
            chunkstore_lib.write(name, df, chunk_size=chunk_size)
        df_list.append(df)

    return pd.concat(df_list)


def test_multiple_actions(chunkstore_lib):
    def helper(chunkstore_lib, name, chunk_size):
        written_df = write_random_data(chunkstore_lib, name, 1, list(range(1, 31)), list(range(1, 101)), chunk_size=chunk_size)

        read_info = chunkstore_lib.read(name)
        assert_frame_equal(written_df, read_info)

        df = write_random_data(chunkstore_lib, name, 1, list(range(1, 31)), list(range(1, 101)), chunk_size=chunk_size)

        read_info = chunkstore_lib.read(name)
        assert_frame_equal(df, read_info)

        r = read_info
        df = write_random_data(chunkstore_lib, name, 2, list(range(1, 29)), list(range(1, 501)), append=True, chunk_size=chunk_size)
        read_info = chunkstore_lib.read(name)
        assert_frame_equal(pd.concat([r, df]), read_info)

    for chunk_size in ['D', 'M', 'Y']:
        helper(chunkstore_lib, 'test_data_' + chunk_size, chunk_size)


def test_multiple_actions_monthly_data(chunkstore_lib):
    def helper(chunkstore_lib, chunk_size, name, df, append):
        chunkstore_lib.write(name, df, chunk_size=chunk_size)

        r = chunkstore_lib.read(name)
        assert_frame_equal(r, df)
        
        chunkstore_lib.append(name, append)

        assert_frame_equal(chunkstore_lib.read(name), pd.concat([df, append]))

        chunkstore_lib.update(name, append)

        if chunk_size is not "Y":
            assert_frame_equal(chunkstore_lib.read(name), pd.concat([df, append]))
        else:
            # chunksize is the entire DF, so we'll overwrite the whole thing
            # with the update when its yearly chunking
            assert_frame_equal(chunkstore_lib.read(name), append)

    df = []
    for month in range(1, 4):
        df.extend(list(gen_daily_data(month, list(range(1, 21)), list(range(1, 11)))))

    df = pd.concat(df)

    append = []
    for month in range(6, 10):
        append.extend(list(gen_daily_data(month, list(range(1, 21)), list(range(1, 11)))))

    append = pd.concat(append)

    for chunk_size in ['D', 'M', 'Y']:
        helper(chunkstore_lib, chunk_size, 'test_monthly_' + chunk_size, df, append)


def test_delete(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3]},
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 1),
                                                 (dt(2016, 1, 2), 1),
                                                 (dt(2016, 1, 3), 1)],
                                                names=['date', 'id'])
                   )
    chunkstore_lib.write('test_df', df)
    read_df = chunkstore_lib.read('test_df')
    assert_frame_equal(df, read_df)
    assert ('test_df' in chunkstore_lib.list_symbols())
    chunkstore_lib.delete('test_df')
    assert (chunkstore_lib.list_symbols() == [])


def test_get_info(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3]},
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 1),
                                                 (dt(2016, 1, 2), 1),
                                                 (dt(2016, 1, 3), 1)],
                                                names=['date', 'id'])
                   )
    chunkstore_lib.write('test_df', df)
    info = {'len': 3,
            'chunk_count': 3,
            'metadata': {'columns': [u'date', u'id', u'data']},
            'chunker': u'date',
            'chunk_size': 'D',
            'serializer': u'FrameToArray'
            }
    assert(chunkstore_lib.get_info('test_df') == info)
    

def test_get_info_after_append(chunkstore_lib):
    df = DataFrame(data={'data': [1.1, 2.1, 3.1]},
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 1),
                                                 (dt(2016, 1, 2), 1),
                                                 (dt(2016, 1, 3), 1)],
                                                names=['date', 'id'])
                   )
    chunkstore_lib.write('test_df', df)
    df2 = DataFrame(data={'data': [1.1, 1.1, 1.1]},
                    index=MultiIndex.from_tuples([(dt(2016, 1, 1), 2),
                                                  (dt(2016, 1, 2), 2),
                                                  (dt(2016, 1, 4), 1)],
                                                 names=['date', 'id'])
                    )
    chunkstore_lib.append('test_df', df2)
    assert_frame_equal(chunkstore_lib.read('test_df'), pd.concat([df, df2]).sort_index())

    info = {'len': 6,
            'chunk_count': 4,
            'metadata': {'columns': [u'date', u'id', u'data']},
            'chunker': u'date',
            'chunk_size': u'D',
            'serializer': u'FrameToArray'
            }

    assert(chunkstore_lib.get_info('test_df') == info)
    

def test_get_info_after_update(chunkstore_lib):
    df = DataFrame(data={'data': [1.1, 2.1, 3.1]},
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 1),
                                                 (dt(2016, 1, 2), 1),
                                                 (dt(2016, 1, 3), 1)],
                                                names=['date', 'id'])
                   )
    chunkstore_lib.write('test_df', df)
    df2 = DataFrame(data={'data': [1.1, 1.1, 1.1]},
                    index=MultiIndex.from_tuples([(dt(2016, 1, 1), 2),
                                                  (dt(2016, 1, 2), 2),
                                                  (dt(2016, 1, 4), 1)],
                                                 names=['date', 'id'])
                    )
    chunkstore_lib.update('test_df', df2)

    info = {'len': 4,
            'chunk_count': 4,
            'metadata': {'columns': [u'date', u'id', u'data']},
            'chunker': u'date',
            'chunk_size': u'D',
            'serializer': u'FrameToArray'
            }

    assert(chunkstore_lib.get_info('test_df') == info)


def test_delete_range(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3, 4, 5, 6]},
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 1),
                                                 (dt(2016, 1, 2), 1),
                                                 (dt(2016, 2, 1), 1),
                                                 (dt(2016, 2, 2), 1),
                                                 (dt(2016, 3, 1), 1),
                                                 (dt(2016, 3, 2), 1)],
                                                names=['date', 'id'])
                   )

    df_result = DataFrame(data={'data': [1, 6]},
                          index=MultiIndex.from_tuples([(dt(2016, 1, 1), 1),
                                                        (dt(2016, 3, 2), 1)],
                                                       names=['date', 'id'])
                          )

    chunkstore_lib.write('test', df, chunk_size='M')
    chunkstore_lib.delete('test', chunk_range=DateRange(dt(2016, 1, 2), dt(2016, 3, 1)))
    assert_frame_equal(chunkstore_lib.read('test'), df_result)
    assert(chunkstore_lib.get_info('test')['len'] == len(df_result))
    assert(chunkstore_lib.get_info('test')['chunk_count'] == 2)


def test_delete_range_noindex(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3, 4, 5, 6],
                         'date': [dt(2016, 1, 1),
                                  dt(2016, 1, 2),
                                  dt(2016, 2, 1),
                                  dt(2016, 2, 2),
                                  dt(2016, 3, 1),
                                  dt(2016, 3, 2)]})

    df_result = DataFrame(data={'data': [1, 6],
                                'date': [dt(2016, 1, 1),
                                         dt(2016, 3, 2)]})

    chunkstore_lib.write('test', df, chunk_size='M')
    chunkstore_lib.delete('test', chunk_range=DateRange(dt(2016, 1, 2), dt(2016, 3, 1)))
    assert_frame_equal(chunkstore_lib.read('test'), df_result)


def test_read_chunk_range(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3, 4, 5, 6, 7, 8, 9]},
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 1),
                                                 (dt(2016, 1, 2), 1),
                                                 (dt(2016, 1, 3), 1),
                                                 (dt(2016, 2, 1), 1),
                                                 (dt(2016, 2, 2), 1),
                                                 (dt(2016, 2, 3), 1),
                                                 (dt(2016, 3, 1), 1),
                                                 (dt(2016, 3, 2), 1),
                                                 (dt(2016, 3, 3), 1)],
                                                names=['date', 'id'])
                   )

    chunkstore_lib.write('test', df, chunk_size='M')
    assert(chunkstore_lib.read('test', chunk_range=DateRange(dt(2016, 1, 1), dt(2016, 1, 1))).index.get_level_values('date')[0] == dt(2016,1,1))
    assert(chunkstore_lib.read('test', chunk_range=DateRange(dt(2016, 1, 2), dt(2016, 1, 2))).index.get_level_values('date')[0] == dt(2016, 1, 2))
    assert(chunkstore_lib.read('test', chunk_range=DateRange(dt(2016, 1, 3), dt(2016, 1, 3))).index.get_level_values('date')[0] == dt(2016, 1, 3))
    assert(chunkstore_lib.read('test', chunk_range=DateRange(dt(2016, 2, 2), dt(2016, 2, 2))).index.get_level_values('date')[0] == dt(2016, 2, 2))

    assert(len(chunkstore_lib.read('test', chunk_range=DateRange(dt(2016, 2, 2), dt(2016, 2, 2)), filter_data=False)) == 3)

    df2 = chunkstore_lib.read('test', chunk_range=DateRange(None, None))
    assert_frame_equal(df, df2)


def test_read_data_doesnt_exist(chunkstore_lib):
    with pytest.raises(NoDataFoundException) as e:
        chunkstore_lib.read('some_data')
    assert('No data found' in str(e))


def test_invalid_type(chunkstore_lib):
    with pytest.raises(Exception) as e:
        chunkstore_lib.write('some_data', str("Cannot write a string"), 'D')
    assert('Can only chunk DataFrames' in str(e))


def test_append_no_data(chunkstore_lib):
    with pytest.raises(NoDataFoundException) as e:
        chunkstore_lib.append('some_data', DataFrame())
    assert('Symbol does not exist.' in str(e))


def test_append_no_new_data(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3, 4, 5, 6, 7, 8, 9]},
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 1),
                                                 (dt(2016, 1, 2), 1),
                                                 (dt(2016, 1, 3), 1),
                                                 (dt(2016, 2, 1), 1),
                                                 (dt(2016, 2, 2), 1),
                                                 (dt(2016, 2, 3), 1),
                                                 (dt(2016, 3, 1), 1),
                                                 (dt(2016, 3, 2), 1),
                                                 (dt(2016, 3, 3), 1)],
                                                names=['date', 'id'])
                   )

    chunkstore_lib.write('test', df)
    chunkstore_lib.append('test', df)
    r = chunkstore_lib.read('test')
    assert_frame_equal(pd.concat([df, df]).sort_index(), r)


def test_overwrite_series(chunkstore_lib):
    s = pd.Series([1], index=pd.date_range('2016-01-01',
                                           '2016-01-01',
                                           name='date'),
                  name='vals')

    chunkstore_lib.write('test', s)
    chunkstore_lib.write('test', s + 1)
    assert_series_equal(chunkstore_lib.read('test'), s + 1)


def test_overwrite_series_monthly(chunkstore_lib):
    s = pd.Series([1, 2], index=pd.Index(data=[dt(2016, 1, 1), dt(2016, 2, 1)], name='date'), name='vals')

    chunkstore_lib.write('test', s, chunk_size='M')
    chunkstore_lib.write('test', s + 1, chunk_size='M')
    assert_series_equal(chunkstore_lib.read('test'), s + 1)


def test_pandas_datetime_index_store_series(chunkstore_lib):
    df = Series(data=[1, 2, 3],
                index=Index(data=[dt(2016, 1, 1),
                                  dt(2016, 1, 2),
                                  dt(2016, 1, 3)],
                            name='date'),
                name='data')
    chunkstore_lib.write('chunkstore_test', df, chunk_size='D')
    s = chunkstore_lib.read('chunkstore_test', chunk_range=DateRange(dt(2016, 1, 1), dt(2016, 1, 3)))
    assert_series_equal(s, df)


def test_yearly_series(chunkstore_lib):
    df = Series(data=[1, 2, 3],
                index=Index(data=[dt(2016, 1, 1),
                                  dt(2016, 2, 1),
                                  dt(2016, 3, 3)],
                            name='date'),
                name='data')

    chunkstore_lib.write('chunkstore_test', df, chunk_size='Y')
    ret = chunkstore_lib.read('chunkstore_test', chunk_range=DateRange(dt(2016, 1, 1), dt(2016, 3, 3)))
    assert_series_equal(df, ret)


def test_store_objects_series(chunkstore_lib):
    df = Series(data=['1', '2', '3'],
                index=Index(data=[dt(2016, 1, 1),
                                  dt(2016, 1, 2),
                                  dt(2016, 1, 3)],
                            name='date'),
                name='data')

    chunkstore_lib.write('chunkstore_test', df, chunk_size='D')
    ret = chunkstore_lib.read('chunkstore_test', chunk_range=DateRange(dt(2016, 1, 1), dt(2016, 1, 3)))
    assert_series_equal(df, ret)


def test_update_series(chunkstore_lib):
    df = Series(data=[1, 2, 3],
                index=pd.Index(data=[dt(2016, 1, 1),
                                     dt(2016, 1, 2),
                                     dt(2016, 1, 3)], name='date'),
                name='data')
    df2 = Series(data=[20, 30, 40],
                 index=pd.Index(data=[dt(2016, 1, 2),
                                      dt(2016, 1, 3),
                                      dt(2016, 1, 4)], name='date'),
                 name='data')

    equals = Series(data=[1, 20, 30, 40],
                    index=pd.Index(data=[dt(2016, 1, 1),
                                         dt(2016, 1, 2),
                                         dt(2016, 1, 3),
                                         dt(2016, 1, 4)], name='date'),
                    name='data')

    chunkstore_lib.write('chunkstore_test', df, chunk_size='D')
    chunkstore_lib.update('chunkstore_test', df2)
    assert_series_equal(chunkstore_lib.read('chunkstore_test'), equals)


def test_update_same_series(chunkstore_lib):
    df = Series(data=[1, 2, 3],
                index=pd.Index(data=[dt(2016, 1, 1),
                                     dt(2016, 1, 2),
                                     dt(2016, 1, 3)], name='date'),
                name='data')
    chunkstore_lib.write('chunkstore_test', df, chunk_size='D')

    sym = chunkstore_lib._get_symbol_info('chunkstore_test')
    chunkstore_lib.update('chunkstore_test', df)
    assert(sym == chunkstore_lib._get_symbol_info('chunkstore_test'))


def test_dtype_mismatch(chunkstore_lib):
    s = pd.Series([1], index=pd.date_range('2016-01-01', '2016-01-01', name='date'), name='vals')

    # Write with an int
    chunkstore_lib.write('test', s, chunk_size='D')
    assert(str(chunkstore_lib.read('test').dtype) == 'int64')

    # Update with a float
    chunkstore_lib.update('test', s * 1.0)
    assert(str(chunkstore_lib.read('test').dtype) == 'float64')

    chunkstore_lib.write('test', s * 1.0, chunk_size='D')
    assert(str(chunkstore_lib.read('test').dtype) == 'float64')


def test_read_column_subset(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3, 4, 5, 6, 7, 8, 9],
                         'open': [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9],
                         'close': [1.2, 2.3, 3.4, 4.5, 5.6, 6.7, 7.8, 8.9, 9.0],
                         'prev_close': [.1, .2, .3, .4, .5, .6, .7, .8, .8],
                         'volume': [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000]
                         },
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 1),
                                                 (dt(2016, 1, 2), 1),
                                                 (dt(2016, 1, 3), 1),
                                                 (dt(2016, 2, 1), 1),
                                                 (dt(2016, 2, 2), 1),
                                                 (dt(2016, 2, 3), 1),
                                                 (dt(2016, 3, 1), 1),
                                                 (dt(2016, 3, 2), 1),
                                                 (dt(2016, 3, 3), 1)],
                                                names=['date', 'id'])
                   )

    chunkstore_lib.write('test', df, chunk_size='D')
    r = chunkstore_lib.read('test', columns=['prev_close', 'volume'])
    assert_frame_equal(r, df[['prev_close', 'volume']])


def test_rename(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3, 4, 5, 6, 7, 8, 9],
                         'open': [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9],
                         'close': [1.2, 2.3, 3.4, 4.5, 5.6, 6.7, 7.8, 8.9, 9.0],
                         'prev_close': [.1, .2, .3, .4, .5, .6, .7, .8, .8],
                         'volume': [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000]
                         },
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 1),
                                                 (dt(2016, 1, 2), 1),
                                                 (dt(2016, 1, 3), 1),
                                                 (dt(2016, 2, 1), 1),
                                                 (dt(2016, 2, 2), 1),
                                                 (dt(2016, 2, 3), 1),
                                                 (dt(2016, 3, 1), 1),
                                                 (dt(2016, 3, 2), 1),
                                                 (dt(2016, 3, 3), 1)],
                                                names=['date', 'id'])
                   )

    chunkstore_lib.write('test', df, chunk_size='D')
    assert_frame_equal(chunkstore_lib.read('test'), df)
    chunkstore_lib.rename('test', 'new_name')
    assert_frame_equal(chunkstore_lib.read('new_name'), df)

    with pytest.raises(Exception) as e:
        chunkstore_lib.rename('new_name', 'new_name')
    assert('already exists' in str(e))

    assert('test' not in chunkstore_lib.list_symbols())

    '''
    read out all chunks that have symbol set to 'test'. List should be empty
    '''
    chunks = []
    for x in chunkstore_lib._collection.find({SYMBOL: 'test'}, sort=[(START, pymongo.ASCENDING)],):
        chunks.append(x)

    assert(len(chunks) == 0)


def test_pass_thru_chunker(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3]})

    chunkstore_lib.write('test_df', df, chunker=PassthroughChunker())
    read_df = chunkstore_lib.read('test_df')
    assert_frame_equal(df, read_df)


def test_pass_thru_chunker_append(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3]})
    df2 = DataFrame(data={'data': [4, 5, 6]})

    chunkstore_lib.write('test_df', df, chunker=PassthroughChunker())
    chunkstore_lib.append('test_df', df2)
    read_df = chunkstore_lib.read('test_df')

    assert_frame_equal(pd.concat([df, df2], ignore_index=True), read_df)


def test_pass_thru_chunker_update(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3]})
    df2 = DataFrame(data={'data': [5, 6, 7]})

    chunkstore_lib.write('test_df', df, chunker=PassthroughChunker())
    chunkstore_lib.update('test_df', df2)
    read_df = chunkstore_lib.read('test_df')

    assert_frame_equal(df2, read_df)


def test_pass_thru_chunker_update_range(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3]})
    df2 = DataFrame(data={'data': [5, 6, 7]})

    chunkstore_lib.write('test_df', df, chunker=PassthroughChunker())
    chunkstore_lib.update('test_df', df2, chunk_range="")
    read_df = chunkstore_lib.read('test_df')

    assert_frame_equal(read_df, df2)


def test_size_chunking(chunkstore_lib):
    df = DataFrame(data={'data': np.random.randint(0, 100, size=5500000),
                         'date': [dt(2016, 1, 1)] * 5500000})

    chunkstore_lib.write('test_df', df)
    read_df = chunkstore_lib.read('test_df')
    assert_frame_equal(df, read_df)


def test_size_chunk_append(chunkstore_lib):
    df = DataFrame(data={'data': np.random.randint(0, 100, size=5500000),
                         'date': [dt(2016, 1, 1)] * 5500000})
    dg = DataFrame(data={'data': np.random.randint(0, 100, size=5500000),
                         'date': [dt(2016, 1, 1)] * 5500000})
    chunkstore_lib.write('test_df', df)
    chunkstore_lib.append('test_df', dg)
    read_df = chunkstore_lib.read('test_df')

    assert_frame_equal(pd.concat([df, dg], ignore_index=True), read_df)


def test_delete_range_segment(chunkstore_lib):
    df = DataFrame(data={'data': np.random.randint(0, 100, size=20000000),
                         'date': [dt(2016, 1, 1)] * 20000000})
    dg = DataFrame(data={'data': np.random.randint(0, 100, size=100),
                         'date': [dt(2016, 1, 2)] * 100})
    chunkstore_lib.write('test_df', pd.concat([df, dg], ignore_index=True), chunk_size='M')
    chunkstore_lib.delete('test_df')
    assert('test_df' not in chunkstore_lib.list_symbols())

    chunkstore_lib.write('test_df', pd.concat([df, dg], ignore_index=True), chunk_size='M')
    chunkstore_lib.delete('test_df', chunk_range=pd.date_range(dt(2016, 1, 1), dt(2016, 1, 1)))
    read_df = chunkstore_lib.read('test_df')
    assert(read_df.equals(dg))
    assert(chunkstore_lib._collection.count({'sy': 'test_df'}) == 1)


def test_size_chunk_update(chunkstore_lib):
    df = DataFrame(data={'data': np.random.randint(0, 100, size=5500000),
                         'date': [dt(2016, 1, 1)] * 5500000})
    dg = DataFrame(data={'data': np.random.randint(0, 100, size=5500000),
                         'date': [dt(2016, 1, 1)] * 5500000})
    dh = DataFrame(data={'data': np.random.randint(0, 100, size=100),
                         'date': [dt(2016, 1, 1)] * 100})
    chunkstore_lib.write('test_df', df)
    chunkstore_lib.append('test_df', dg)
    chunkstore_lib.update('test_df', dh)

    read_df = chunkstore_lib.read('test_df')

    assert_frame_equal(dh, read_df)
    assert(chunkstore_lib._collection.count({'sy': 'test_df'}) == 1)


def test_size_chunk_multiple_update(chunkstore_lib):
    df_large = DataFrame(data={'data': np.random.randint(0, 100, size=5500000),
                               'date': [dt(2015, 1, 1)] * 5500000})
    df_small = DataFrame(data={'data': np.random.randint(0, 100, size=100),
                               'date': [dt(2016, 1, 1)] * 100})
    chunkstore_lib.update('test_df', df_large, upsert=True)
    chunkstore_lib.update('test_df', df_small, upsert=True)

    read_df = chunkstore_lib.read('test_df')

    expected = pd.concat([df_large, df_small]).reset_index(drop=True)

    assert_frame_equal(expected, read_df)
    assert(chunkstore_lib._collection.count({'sy': 'test_df'}) == 3)


def test_get_chunk_range(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3]},
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 1),
                                                 (dt(2016, 1, 2), 1),
                                                 (dt(2016, 1, 3), 1)],
                                                names=['date', 'id'])
                   )
    chunkstore_lib.write('test_df', df, chunk_size='D')
    x = list(chunkstore_lib.get_chunk_ranges('test_df'))
    assert(len(x) == 3)
    assert((b'2016-01-01', b'2016-01-01') in x)
    assert((b'2016-01-02', b'2016-01-02') in x)
    assert((b'2016-01-03', b'2016-01-03') in x)


def test_iterators(chunkstore_lib):
    df = DataFrame(data={'data': [1, 2, 3]},
                   index=MultiIndex.from_tuples([(dt(2016, 1, 1), 1),
                                                 (dt(2016, 1, 2), 1),
                                                 (dt(2016, 1, 3), 1)],
                                                names=['date', 'id'])
                   )
    chunkstore_lib.write('test_df', df, chunk_size='D')

    for x, d in enumerate(chunkstore_lib.iterator('test_df')):
        assert(len(d) == 1)
        assert(d.data[0] == x + 1)

    for x, d in enumerate(chunkstore_lib.reverse_iterator('test_df')):
        assert(len(d) == 1)
        assert(d.data[0] == len(df) - x)

    dr = DateRange(dt(2016, 1, 2), dt(2016, 1, 2))
    assert(len(list(chunkstore_lib.iterator('test_df', chunk_range=dr))) == 1)
    assert(len(list(chunkstore_lib.reverse_iterator('test_df', chunk_range=dr))) == 1)
