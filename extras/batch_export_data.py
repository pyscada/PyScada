#!/usr/bin/env python
# -*- coding: utf-8 -*-



from pyscada.export.export import export_recordeddata_to_file


export_recordeddata_to_file(options['start_id'],options['stop_id'],os.path.abspath(options['filename']))