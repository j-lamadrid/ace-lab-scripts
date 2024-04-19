import pandas as pd
import numpy as np
import re

import warnings
warnings.filterwarnings('ignore')

class EyeTrackingSheet():
    
    
    def __init__(self, 
                 fp, 
                 master_fp, 
                 et_summary_fp, 
                 lwr_fp, 
                 timeline, 
                 software):
        
        self.fp = fp
        
        self.df = pd.read_csv(fp, sep='\t', header=0)
        
        if timeline == 'Traffic':
            self.df = self.df[~self.df['Recording'].str.lower().str.contains('test')]
            self.df = self.df[~self.df['Recording'].str.lower().str.contains('ys')]
            self.df = self.df[~self.df['Recording'].str.lower().str.contains('ca')]
        else:
            self.df = self.df[~self.df['Participant'].str.lower().str.contains('test')]
            self.df = self.df[~self.df['Participant'].str.lower().str.contains('ys')]
            self.df = self.df[~self.df['Participant'].str.lower().str.contains('ca')]
        
        self.master_df = pd.read_excel(master_fp)
        
        self.et_summary_df = pd.read_excel(et_summary_fp)
        
        self.lwr_df = pd.read_csv(lwr_fp)
        
        self.timeline = timeline
        
        self.software = software
        
        if timeline == 'Traffic':
            self.geo_tag = self.df['Media'][0][-1]
            self.soc_tag = 'R' if self.geo_tag == 'L' else 'L'
        else:
            self.geo_tag = self.df['TOI'][0][-1]
            self.soc_tag = 'R' if self.geo_tag == 'L' else 'L'
        
        self.generated_df = None
    
    
    def generate(self):
        
        df = self.df.copy()
        
        to_divide_idx = (pd.Series(df.columns).apply(lambda s: s.lower()).str.contains('time') + 
                 pd.Series(df.columns).apply(lambda s: s.lower()).str.contains('duration') +
                 pd.Series(df.columns).apply(lambda s: s.lower()).str.contains('interval')
                )
        
        to_divide = df.columns[to_divide_idx][1:]
        
        for c in to_divide:
            try:
                df[c] = df[c].astype(float) / 1000
            except:
                pass
            
        if self.timeline == 'Geo':
            
            geo_dur = df['Total_duration_of_fixations.Geo-' + self.geo_tag]
            soc_dur = df['Total_duration_of_fixations.Soc-' + self.soc_tag]
            geo_fix = df['Number_of_fixations.Geo-' + self.geo_tag]
            soc_fix = df['Number_of_fixations.Soc-' + self.soc_tag]
            geo_sac = df['Number_of_saccades_in_AOI.Geo-' + self.geo_tag]
            soc_sac = df['Number_of_saccades_in_AOI.Soc-' + self.soc_tag]

            tol_fix_dur = geo_dur + soc_dur
            per_fix_geo = geo_dur / tol_fix_dur
            per_fix_soc = soc_dur / tol_fix_dur
            num_sac_geo = geo_fix - 1
            num_sac_soc = soc_fix - 1
            num_sac_sec_geo = num_sac_geo / geo_dur
            num_sac_sec_soc = num_sac_soc / soc_dur

            df['Total Fixation Duration'] = tol_fix_dur
            df['% Fixation Geo'] = per_fix_geo * 100
            df['% Fixation Social'] = per_fix_soc * 100
            df['# Saccades Geo (n-1 fixations)'] = num_sac_geo
            df['# Saccades Social (n-1 fixations)'] = num_sac_soc
            df['Saccades per Second Geo'] = num_sac_sec_geo
            df['Saccades Per Second Social'] = num_sac_sec_soc

            df['# Saccades Geo (Tobii Pro Lab)'] = geo_sac
            df['# Saccades Social(Tobii Pro Lab)'] = soc_sac

            df['Saccades per Second Geo (Tobii Pro Lab)'] = geo_sac / geo_dur
            df['Saccades Per Second Social (Tobii Pro Lab)'] = soc_sac / soc_dur

            df['Number_of_fixations_WholeMovie_GEO'] = df['Number_of_fixations.Geo-' + self.geo_tag]
            df['Fixation Duration_WholeMovie_GEO_mean'] = df['Average_duration_of_fixations.Geo-' + self.geo_tag]
            df['Fixation Duration_WholeMovie_GEO_sum'] = df['Total_duration_of_fixations.Geo-' + self.geo_tag]

            df['Number_of_fixations_WholeMovie_SOC'] = df['Number_of_fixations.Soc-' + self.soc_tag]
            df['Fixation Duration_WholeMovie_SOC_mean'] = df['Average_duration_of_fixations.Soc-' + self.soc_tag]
            df['Fixation Duration_WholeMovie_SOC_sum'] = df['Total_duration_of_fixations.Soc-' + self.soc_tag]
            
            self.generated_df = df[self.master_df.columns[25:-1]]
            
            self.generated_df['Recording Name'] = df['Participant']
        
        elif self.timeline == 'Soc':
            
            geo_dur = df['Total_duration_of_fixations.Geo-' + self.geo_tag]
            soc_dur = df['Total_duration_of_fixations.Soc-' + self.soc_tag]
            geo_fix = df['Number_of_fixations.Geo-' + self.geo_tag]
            soc_fix = df['Number_of_fixations.Soc-' + self.soc_tag]
            geo_sac = df['Number_of_saccades_in_AOI.Geo-' + self.geo_tag]
            soc_sac = df['Number_of_saccades_in_AOI.Soc-' + self.soc_tag]

            tol_fix_dur = geo_dur + soc_dur
            per_fix_geo = geo_dur / tol_fix_dur
            per_fix_soc = soc_dur / tol_fix_dur
            num_sac_geo = geo_fix - 1
            num_sac_soc = soc_fix - 1
            num_sac_sec_geo = num_sac_geo / geo_dur
            num_sac_sec_soc = num_sac_soc / soc_dur

            df['Total Fixation Duration'] = tol_fix_dur
            df['% Fixation Geo '] = per_fix_geo * 100
            df['% Fixation Socia'] = per_fix_soc * 100
            df['# Saccades Geo (n-1 fixations)'] = num_sac_geo
            df['# Saccades Social (n-1 fixations)'] = num_sac_soc
            df['Saccades per Second Geo (n-1 fixations)'] = num_sac_sec_geo
            df['Saccades Per Second Social (n-1 fixations)'] = num_sac_sec_soc

            df['# Saccades Geo (Tobii Pro Lab)'] = geo_sac
            df['# Saccades Social(Tobii Pro Lab)'] = soc_sac

            df['Saccades per Second Geo'] = geo_sac / geo_dur
            df['Saccades Per Second Social'] = soc_sac / soc_dur

            df['Number_of_fixations_Whole Movie_Geo R_N'] = df['Number_of_fixations.Geo-' + self.geo_tag]
            df['Fixation Duration_Whole Movie_Geo R_Mean'] = df['Average_duration_of_fixations.Geo-' + self.geo_tag]
            df['Fixation Duration_Whole Movie_Geo R_Sum'] = df['Total_duration_of_fixations.Geo-' + self.geo_tag]

            df['Number_of_fixations_Whole Movie_Soc L_N'] = df['Number_of_fixations.Soc-' + self.soc_tag]
            df['Fixation Duration_Whole Movie_Soc L_Mean'] = df['Average_duration_of_fixations.Soc-' + self.soc_tag]
            df['Fixation Duration_Whole Movie_Soc L_Sum'] = df['Total_duration_of_fixations.Soc-' + self.soc_tag]
            
            self.generated_df = df[self.master_df.columns[19:-1]]
            self.generated_df['Recording'] = df['Recording']
            self.generated_df['Participant'] = df['Participant']
        
        elif self.timeline == 'Play':
            
            geo_dur = df['Total_duration_of_fixations.Geo-' + self.geo_tag]
            soc_dur = df['Total_duration_of_fixations.Soc-' + self.soc_tag]
            geo_fix = df['Number_of_fixations.Geo-' + self.geo_tag]
            soc_fix = df['Number_of_fixations.Soc-' + self.soc_tag]
            geo_sac = df['Number_of_saccades_in_AOI.Geo-' + self.geo_tag]
            soc_sac = df['Number_of_saccades_in_AOI.Soc-' + self.soc_tag]

            tol_fix_dur = geo_dur + soc_dur
            per_fix_geo = geo_dur / tol_fix_dur
            per_fix_soc = soc_dur / tol_fix_dur
            num_sac_geo = geo_fix - 1
            num_sac_soc = soc_fix - 1
            num_sac_sec_geo = num_sac_geo / geo_dur
            num_sac_sec_soc = num_sac_soc / soc_dur
            
            df['Total Fixation Duration'] = tol_fix_dur
            df['% Fixation Geo'] = per_fix_geo * 100
            df['% Fixation Social'] = per_fix_soc * 100
            df['# Saccades Geo (n-1 fixations)'] = num_sac_geo
            df['# Saccades Social (n-1 fixations)'] = num_sac_soc
            df['Saccades per Second Geo (n-1 fixations)'] = num_sac_sec_geo
            df['Saccades Per Second Social (n-1 fixations)'] = num_sac_sec_soc

            df['# Saccades Geo (Tobii Pro Lab)'] = geo_sac
            df['# Saccades Social(Tobii Pro Lab)'] = soc_sac


            df['Number_of_fixations_Whole Movie_Geo_N'] = df['Number_of_fixations.Geo-' + self.geo_tag]
            df['Fixation Duration_Whole Movie_Geo_Mean'] = df['Average_duration_of_fixations.Geo-' + self.geo_tag]
            df['Fixation Duration_Whole Movie_Geo_Sum'] = df['Total_duration_of_fixations.Geo-' + self.geo_tag]

            df['Number_of_fixations_Whole Movie_Soc _N'] = df['Number_of_fixations.Soc-' + self.soc_tag]
            df['Fixation Duration_Whole Movie_Soc_Mean'] = df['Average_duration_of_fixations.Soc-' + self.soc_tag]
            df['Fixation Duration_Whole Movie_Soc_Sum'] = df['Total_duration_of_fixations.Soc-' + self.soc_tag]
            
            self.generated_df = df[self.master_df.columns[19:-1]]
            self.generated_df['Recording'] = df['Recording']
            self.generated_df['Participant'] = df['Participant']
        
        elif self.timeline == 'Traffic':
            
            m_dur = df['Total_duration_of_fixations.Motherese-' + self.geo_tag]
            t_dur = df['Total_duration_of_fixations.Traffic-' + self.soc_tag]
            m_fix = df['Number_of_fixations.Motherese-' + self.geo_tag]
            t_fix = df['Number_of_fixations.Traffic-' + self.soc_tag]
            m_sac = df['Number_of_saccades_in_AOI.Motherese-' + self.geo_tag]
            t_sac = df['Number_of_saccades_in_AOI.Traffic-' + self.soc_tag]

            tol_fix_dur = m_dur + t_dur
            per_fix_m = m_dur / tol_fix_dur
            per_fix_t = t_dur / tol_fix_dur
            num_sac_m = m_fix - 1
            num_sac_t = t_fix - 1
            num_sac_sec_m = num_sac_m / m_dur
            num_sac_sec_t = num_sac_t / t_dur
            
            df['Total'] = tol_fix_dur
            df['% Fixation Motherese'] = per_fix_m * 100
            df['% Fixation Traffic'] = per_fix_t * 100
            df['# Saccades (n-1 Fixations) QL Motherese'] = num_sac_m
            df['# Saccades (n-1 Fixations) Traffic'] = num_sac_t
            df['Saccades Per Second Motherese'] = num_sac_sec_m
            df['Saccades Per Second Traffic'] = num_sac_sec_t

            df['Number_of_saccades_in_AOI-QLmotherese'] = m_sac
            df['Number_of_saccades_in_AOI-Traffic'] = t_sac


            df['Number_of_Fixations_QL Motherese_N'] = df['Number_of_fixations.Motherese-' + self.geo_tag]
            df['Fixation Duration_Whole Movie_QL Motherese _Mean'] = df['Average_duration_of_fixations.Motherese-' + self.geo_tag]
            df['Fixation Duration_Whole Movie_QL Motherese _Sum'] = df['Total_duration_of_fixations.Motherese-' + self.geo_tag]

            df['Number_of_Fixations_Traffic _N'] = df['Number_of_fixations.Traffic-' + self.soc_tag]
            df['Fixation Duration_Whole Movie_Traffic _Mean'] = df['Average_duration_of_fixations.Traffic-' + self.soc_tag]
            df['Fixation Duration_Whole Movie_Traffic _Sum'] = df['Total_duration_of_fixations.Traffic-' + self.soc_tag]
            
            df['Fixation.Duration_Whole.Scene_Background_.AboveGrayCat_Sum'] = df['Total_duration_of_fixations.Background_AboveGrayCat']
            df['Fixation.Duration_Whole.Scene_Background_AboveOrangeCat_Sum'] = df['Total_duration_of_fixations.Background_AboveOrangeCat']
            df['Fixation.Duration_Whole.Scene_Background_Forehead_Sum'] = df['Total_duration_of_fixations.Background_Forehead']
            df['Fixation.Duration_Whole.Scene_Background_ShoulderArea_Sum'] = df['Total_duration_of_fixations.Background_ShoulderArea']
            df['Fixation.Duration_Whole.Scene_Eyes_Sum'] = df['Total_duration_of_fixations.Eyes']
            df['Fixation.Duration_Whole.Scene_Face_Sum'] = df['Total_duration_of_fixations.Face']
            df['Fixation.Duration_Whole.Scene_Mouth_Sum'] = df['Total_duration_of_fixations.Mouth']
            df['Fixation.Duration_Whole.Scene_Object_GrayCat_Sum'] = df['Total_duration_of_fixations.Object_GrayCat']
            df['Fixation.Duration_Whole.Scene_Object_OrangeCat_Sum'] = df['Total_duration_of_fixations.Object_OrangeCat']
            
            total_fix = (df['Fixation.Duration_Whole.Scene_Background_.AboveGrayCat_Sum'] +
                         df['Fixation.Duration_Whole.Scene_Background_AboveOrangeCat_Sum'] +
                         df['Fixation.Duration_Whole.Scene_Background_Forehead_Sum'] +
                         df['Fixation.Duration_Whole.Scene_Background_ShoulderArea_Sum'] +
                         df['Fixation.Duration_Whole.Scene_Eyes_Sum'] +
                         df['Fixation.Duration_Whole.Scene_Face_Sum'] +
                         df['Fixation.Duration_Whole.Scene_Mouth_Sum'] +
                         df['Fixation.Duration_Whole.Scene_Object_GrayCat_Sum'] +
                         df['Fixation.Duration_Whole.Scene_Object_OrangeCat_Sum'])
            
            df['Percent.FIX_Background_.AboveGrayCat'] = 100 * df['Fixation.Duration_Whole.Scene_Background_.AboveGrayCat_Sum'] / total_fix
            df['Percent.FIX_Background_AboveOrangeCat'] = 100 * df['Fixation.Duration_Whole.Scene_Background_AboveOrangeCat_Sum'] / total_fix
            df['Percent.FIX_Background_Forehead'] = 100 * df['Fixation.Duration_Whole.Scene_Background_Forehead_Sum'] / total_fix
            df['Percent.FIX_Background_ShoulderArea'] = 100 * df['Fixation.Duration_Whole.Scene_Background_ShoulderArea_Sum'] / total_fix
            df['Percent.FIX_Eyes'] = 100 * df['Fixation.Duration_Whole.Scene_Eyes_Sum'] / total_fix
            df['Percent.FIX_Face'] = 100 * df['Fixation.Duration_Whole.Scene_Face_Sum'] / total_fix
            df['Percent.FIX_Mouth'] = 100 * df['Fixation.Duration_Whole.Scene_Mouth_Sum'] / total_fix
            df['Percent.FIX_Object_GrayCat'] = 100 * df['Fixation.Duration_Whole.Scene_Object_GrayCat_Sum'] / total_fix
            df['Percent.FIX_Object_OrangeCat'] = 100 * df['Fixation.Duration_Whole.Scene_Object_OrangeCat_Sum'] / total_fix
            
            self.generated_df = df[self.master_df.columns[19:-1]]
            self.generated_df['Recording Name'] = df['Recording']
            self.generated_df['Participant'] = df['Participant']
        
        def split_participant(column):
            subject_id = column.apply(lambda data: data[:5])
            date = column.apply(lambda data: pd.to_datetime(data[6:]))
            return subject_id, date
        
        if self.timeline == 'Traffic':
            self.generated_df['Subject ID'], self.generated_df['Date of Eye-tracking'] = split_participant(df['Recording'])
        else:
            self.generated_df['Subject ID'], self.generated_df['Date of Eye-tracking'] = split_participant(df['Participant'])
        
        try:
            pattern = r'Tobii Project (\d+)'
            match = re.search(pattern, self.fp)
            project = match.group(0)
        except:
            pattern = r'Project (\d+)'
            match = re.search(pattern, self.fp)
            project = match.group(0)
        
        if self.timeline == 'Geo':
            self.generated_df['Type of Video'] = 'Geo-' + self.geo_tag + ', ' + 'Soc-' + self.soc_tag
        elif self.timeline == 'Soc' or self.timeline == 'Play':
            self.generated_df['Video Type'] = 'Geo-' + self.geo_tag + ', ' + 'Soc-' + self.soc_tag
        elif self.timeline == 'Traffic':
            self.generated_df['VideoType'] = 'Motherese-' + self.geo_tag + ', ' + 'Traffic-' + self.soc_tag
        
        if self.timeline == 'Traffic':
            self.generated_df['Project #'] = ['Motherese vs Traffic ' + project] * self.generated_df.shape[0]
        else:
            self.generated_df['Project #'] = [project] * self.generated_df.shape[0]
            
        self.generated_df['Tobii Studio vs. Pro Lab'] = [self.software] * self.generated_df.shape[0]
        self.generated_df['DATA SOURCE'] = [np.nan] * self.generated_df.shape[0]
        self.generated_df['In Mastersheet?'] = [np.nan] * self.generated_df.shape[0]
        
        if self.timeline == 'Geo':
            self.generated_df['LONGITUDINAL/SINGLE'] = [np.nan] * self.generated_df.shape[0]
        elif self.timeline == 'Soc' or self.timeline == 'Play' or self.timeline == 'Traffic':
            self.generated_df['Longitudinal/Exclude'] = [np.nan] * self.generated_df.shape[0]
        
        return self.generated_df
        
        
    def fill(self):
        
        if self.timeline == 'Geo':
            
            self.lwr_df.rename(columns={'subjectid': 'Subject ID'}, inplace=True)
            merged_df = pd.merge(self.generated_df, 
                                 self.lwr_df[['Subject ID', 'DOB', 
                                              'vine_p2f2', 'gender', 
                                              'recentDxJ', 'recentDxJ_dxCode', 
                                              'recentDxJ_evalDate', 'recentDxJ_ageMo']], 
                                 on='Subject ID')

            self.et_summary_df.rename(columns={'subjectid': 'Subject ID'}, inplace=True)
            self.et_summary_df['Vision Abnormalities/Notes'] = (self.et_summary_df['vision_bbnormalities'] + 
                                                                ', ' + 
                                                                self.et_summary_df['vision_Abnormalities_Comnts'])

            merged_df = pd.merge(merged_df, self.et_summary_df[['Subject ID', 'Vision Abnormalities/Notes', 
                                                                'final_calibration_quality', 'quality',
                                                                'ageMo']], on='Subject ID')

            merged_df['final_calibration_quality'] = merged_df['final_calibration_quality'].apply(lambda s: s.split(':')[0])
            merged_df['Unnamed: 7'] = [np.nan] * merged_df.shape[0]
            merged_df['1ST_GOOD/OTHER_TIMEPOINT/EXCLUDE'] = [np.nan] * merged_df.shape[0]
            merged_df['Recent DxJ Code Number'] = [np.nan] * merged_df.shape[0]
            merged_df['Twin/Sib'] = [np.nan] * merged_df.shape[0]
            merged_df['Mz/Dz Twin'] = [np.nan] * merged_df.shape[0]
            
            merge_track = self.master_df['Merge#'].values[-1] + 1

            merge_num = []
            while len(merge_num) < merged_df.shape[0]:
                merge_num.append(merge_track)
                merge_track += 1

            merged_df['Merge#'] = merge_num

            merged_df.rename(columns={'ageMo': 'Age at ET'}, inplace=True)
            merged_df.rename(columns={'vine_p2f2': 'P2F2'}, inplace=True)
            merged_df.rename(columns={'gender': 'Sex'}, inplace=True)
            merged_df.rename(columns={'recentDxJ_evalDate': 'Recent Dx evalDate'}, inplace=True)
            merged_df.rename(columns={'recentDxJ_ageMo': 'Recent Dx Age'}, inplace=True)
            merged_df.rename(columns={'recentDxJ': 'Recent DxJ'}, inplace=True)
            merged_df.rename(columns={'recentDxJ_dxCode': 'Recent DxJ Code'}, inplace=True)
            merged_df.rename(columns={'quality': 'Data Quality'}, inplace=True)
            merged_df.rename(columns={'final_calibration_quality': 'Calibration Quality'}, inplace=True)
            merged_df['Recent Dx Age'] = ((pd.to_datetime(merged_df['Recent Dx evalDate']) - pd.to_datetime(merged_df['DOB'])) / 
                                          pd.Timedelta(days=365) * 12).apply(lambda age: round(age, 2))
            merged_df['Age at ET'] = ((merged_df['Date of Eye-tracking'] - pd.to_datetime(merged_df['DOB'])) / pd.Timedelta(days=365) * 12).apply(lambda age: round(age, 2))

            final_ids = merged_df['Subject ID'].values
            original_ids = self.generated_df['Subject ID'].values
            for sid in original_ids:
                if sid not in final_ids:
                    print(sid + ' NOT IN LWR, DATA NOT TRANSFERRED')
        
        elif self.timeline == 'Soc':
            
            self.lwr_df.rename(columns={'subjectid': 'Subject ID'}, inplace=True)
            merged_df = pd.merge(self.generated_df, 
                                 self.lwr_df[['Subject ID', 'DOB', 
                                              'gender', 
                                              'recentDxJ', 'recentDxJ_dxCode', 
                                              'recentDxJ_evalDate', 'recentDxJ_ageMo']], 
                                 on='Subject ID')

            self.et_summary_df.rename(columns={'subjectid': 'Subject ID'}, inplace=True)
            self.et_summary_df['Vision Abnormalities/Notes'] = (self.et_summary_df['vision_bbnormalities'] + 
                                                                ', ' + 
                                                                self.et_summary_df['vision_Abnormalities_Comnts'])

            merged_df = pd.merge(merged_df, self.et_summary_df[['Subject ID', 'Vision Abnormalities/Notes', 
                                                                'final_calibration_quality', 'quality',
                                                                'ageMo']], on='Subject ID')

            merged_df['final_calibration_quality'] = merged_df['final_calibration_quality'].apply(lambda s: s.split(':')[0])
            merged_df['DxJ Code Number'] = [np.nan] * merged_df.shape[0]
            
            merge_track = self.master_df['Merge Number'].values[-1] + 1

            merge_num = []
            while len(merge_num) < merged_df.shape[0]:
                merge_num.append(merge_track)
                merge_track += 1

            merged_df['Merge Number'] = merge_num
            
            merged_df.rename(columns={'DOB': 'Date of Birth'}, inplace=True)
            merged_df.rename(columns={'ageMo': 'ET Age'}, inplace=True)
            merged_df.rename(columns={'gender': 'Sex'}, inplace=True)
            merged_df.rename(columns={'recentDxJ_evalDate': 'Recent Dx Date'}, inplace=True)
            merged_df.rename(columns={'recentDxJ_ageMo': 'Recent Dx Age'}, inplace=True)
            merged_df.rename(columns={'recentDxJ': 'Recent DxJ'}, inplace=True)
            merged_df.rename(columns={'recentDxJ_dxCode': 'Recent DxJ Code'}, inplace=True)
            merged_df.rename(columns={'quality': 'Data Quality'}, inplace=True)
            merged_df.rename(columns={'final_calibration_quality': 'Calibration Quality'}, inplace=True)
            merged_df.rename(columns={'Vision Abnormalities/Notes': 'Vision Abnormalities'}, inplace=True)
            merged_df.rename(columns={'Date of Eye-tracking': 'ET Date'}, inplace=True)
            merged_df['Recent Dx Age'] = ((pd.to_datetime(merged_df['Recent Dx Date']) - pd.to_datetime(merged_df['Date of Birth'])) / 
                                          pd.Timedelta(days=365) * 12).apply(lambda age: round(age, 2))
            merged_df['ET Age'] = ((merged_df['ET Date'] - pd.to_datetime(merged_df['Date of Birth'])) / pd.Timedelta(days=365) * 12).apply(lambda age: round(age, 2))

            final_ids = merged_df['Subject ID'].values
            original_ids = self.generated_df['Subject ID'].values
            for sid in original_ids:
                if sid not in final_ids:
                    print(sid + ' NOT IN LWR, DATA NOT TRANSFERRED')
                    
        elif self.timeline == 'Play':
            
            self.lwr_df.rename(columns={'subjectid': 'Subject ID'}, inplace=True)
            merged_df = pd.merge(self.generated_df, 
                                 self.lwr_df[['Subject ID', 'DOB', 
                                              'gender', 
                                              'recentDxJ', 'recentDxJ_dxCode', 
                                              'recentDxJ_evalDate', 'recentDxJ_ageMo']], 
                                 on='Subject ID')

            self.et_summary_df.rename(columns={'subjectid': 'Subject ID'}, inplace=True)
            self.et_summary_df['Vision Abnormalities/Notes'] = (self.et_summary_df['vision_bbnormalities'] + 
                                                                ', ' + 
                                                                self.et_summary_df['vision_Abnormalities_Comnts'])

            merged_df = pd.merge(merged_df, self.et_summary_df[['Subject ID', 'Vision Abnormalities/Notes', 
                                                                'final_calibration_quality', 'quality',
                                                                'ageMo']], on='Subject ID')

            merged_df['final_calibration_quality'] = merged_df['final_calibration_quality'].apply(lambda s: s.split(':')[0])
            merged_df['Recent Dx Code Number'] = [np.nan] * merged_df.shape[0]
            
            merge_track = self.master_df['Notes'].values[-1] + 1

            merge_num = []
            while len(merge_num) < merged_df.shape[0]:
                merge_num.append(merge_track)
                merge_track += 1

            merged_df['Notes'] = merge_num
            
            merged_df.rename(columns={'DOB': 'Date of Birth'}, inplace=True)
            merged_df.rename(columns={'ageMo': 'ET Age'}, inplace=True)
            merged_df.rename(columns={'gender': 'Sex'}, inplace=True)
            merged_df.rename(columns={'recentDxJ_evalDate': 'Recent DxDate'}, inplace=True)
            merged_df.rename(columns={'recentDxJ_ageMo': 'Recent Dx Age'}, inplace=True)
            merged_df.rename(columns={'recentDxJ': 'Recent DxJ'}, inplace=True)
            merged_df.rename(columns={'recentDxJ_dxCode': 'Recent DxJ Code'}, inplace=True)
            merged_df.rename(columns={'quality': 'Data Quality'}, inplace=True)
            merged_df.rename(columns={'final_calibration_quality': 'Calibration Quality'}, inplace=True)
            merged_df.rename(columns={'Vision Abnormalities/Notes': 'Vision'}, inplace=True)
            merged_df.rename(columns={'Date of Eye-tracking': 'ET Date'}, inplace=True)
            merged_df['Recent Dx Age'] = ((pd.to_datetime(merged_df['Recent DxDate']) - pd.to_datetime(merged_df['Date of Birth'])) / 
                                          pd.Timedelta(days=365) * 12).apply(lambda age: round(age, 2))
            merged_df['ET Age'] = ((merged_df['ET Date'] - pd.to_datetime(merged_df['Date of Birth'])) / pd.Timedelta(days=365) * 12).apply(lambda age: round(age, 2))

            final_ids = merged_df['Subject ID'].values
            original_ids = self.generated_df['Subject ID'].values
            for sid in original_ids:
                if sid not in final_ids:
                    print(sid + ' NOT IN LWR, DATA NOT TRANSFERRED')
                    
        elif self.timeline == 'Traffic':
            
            self.lwr_df.rename(columns={'subjectid': 'Subject ID'}, inplace=True)
            merged_df = pd.merge(self.generated_df, 
                                 self.lwr_df[['Subject ID', 'DOB', 
                                              'gender', 
                                              'recentDxJ', 'recentDxJ_dxCode', 
                                              'recentDxJ_evalDate', 'recentDxJ_ageMo']], 
                                 on='Subject ID')

            self.et_summary_df.rename(columns={'subjectid': 'Subject ID'}, inplace=True)
            self.et_summary_df['Vision Abnormalities/Notes'] = (self.et_summary_df['vision_bbnormalities'] + 
                                                                ', ' + 
                                                                self.et_summary_df['vision_Abnormalities_Comnts'])

            merged_df = pd.merge(merged_df, self.et_summary_df[['Subject ID', 'Vision Abnormalities/Notes', 
                                                                'final_calibration_quality', 'quality',
                                                                'ageMo']], on='Subject ID')

            merged_df['final_calibration_quality'] = merged_df['final_calibration_quality'].apply(lambda s: s.split(':')[0])
            merged_df['Recent DxJ Number'] = [np.nan] * merged_df.shape[0]
            merged_df['Data Comments'] = [np.nan] * merged_df.shape[0]
            
            merge_track = self.master_df['Merge Number'].values[-1] + 1

            merge_num = []
            while len(merge_num) < merged_df.shape[0]:
                merge_num.append(int(merge_track))
                merge_track += 1

            merged_df['Merge Number'] = merge_num
            
            merged_df.rename(columns={'ageMo': 'ET Age'}, inplace=True)
            merged_df.rename(columns={'gender': 'Sex'}, inplace=True)
            merged_df.rename(columns={'quality': 'Data Quality'}, inplace=True)
            merged_df.rename(columns={'final_calibration_quality': 'Calibration Quality'}, inplace=True)
            merged_df.rename(columns={'Vision Abnormalities/Notes': 'Vision Abnormalities'}, inplace=True)
            merged_df.rename(columns={'Date of Eye-tracking': 'ET Date'}, inplace=True)
            merged_df['recentDxJ_ageMo'] = ((pd.to_datetime(merged_df['recentDxJ_evalDate']) - pd.to_datetime(merged_df['DOB'])) / 
                                            pd.Timedelta(days=365) * 12).apply(lambda age: round(age, 2))
            merged_df['ET Age'] = ((merged_df['ET Date'] - pd.to_datetime(merged_df['DOB'])) / pd.Timedelta(days=365) * 12).apply(lambda age: round(age, 2))

            final_ids = merged_df['Subject ID'].values
            original_ids = self.generated_df['Subject ID'].values
            for sid in original_ids:
                if sid not in final_ids:
                    print(sid + ' NOT IN LWR, DATA NOT TRANSFERRED')
        
        self.generated_df = merged_df
        
        return self.generated_df
        
        
    def push(self):
        
        self.generated_df = self.generated_df[self.master_df.columns]

        self.master_df = pd.concat([self.master_df, self.generated_df], ignore_index=True)
        
        if self.timeline == 'Geo':
            rounded_et = []
            rounded_dxj = []
            for i in range(len(self.master_df['Age at ET'])):
                try:
                    rounded_et.append(round(float(self.master_df['Age at ET'][i]), 2))
                    rounded_dxj.append(round(float(self.master_df['Recent Dx Age'][i]), 2))
                except:
                    rounded_et.append(np.nan)
                    rounded_dxj.append(np.nan)
            self.master_df['Age at ET'] = rounded_et
            self.master_df['Recent Dx Age'] = rounded_dxj
            
        elif self.timeline == 'Soc' or self.timeline == 'Play':
            rounded_et = []
            rounded_dxj = []
            for i in range(len(self.master_df['ET Age'])):
                try:
                    rounded_et.append(round(float(self.master_df['ET Age'][i]), 2))
                    rounded_dxj.append(round(float(self.master_df['Recent Dx Age'][i]), 2))
                except:
                    rounded_et.append(np.nan)
                    rounded_dxj.append(np.nan)
            self.master_df['ET Age'] = rounded_et
            self.master_df['Recent Dx Age'] = rounded_dxj
        
        elif self.timeline == 'Traffic':
            rounded_et = []
            rounded_dxj = []
            for i in range(len(self.master_df['ET Age'])):
                try:
                    rounded_et.append(round(float(self.master_df['ET Age'][i]), 2))
                    rounded_dxj.append(round(float(self.master_df['recentDxJ_ageMo'][i]), 2))
                except:
                    rounded_et.append(np.nan)
                    rounded_dxj.append(np.nan)
            self.master_df['ET Age'] = rounded_et
            self.master_df['recentDxJ_ageMo'] = rounded_dxj
            
        return self.master_df