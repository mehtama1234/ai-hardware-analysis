"""Focused HPCA walkthrough of ISP/software cooperation for adaptive vision."""

PDF = 'https://upcommons.upc.edu/bitstreams/5418accb-08a4-45ad-a516-bd3a202115e3/download'

IRIS = {
    'id': 'iris-2025',
    'route': 'hpca-2025',
    'title': 'IRIS: keep detail where the vision task needs it',
    'identity': 'Raúl Taranco, José-María Arnau, Antonio González · IRIS: Unleashing ISP-Software Cooperation to Optimize the Machine Vision Pipeline · HPCA 2025',
    'scope': 'A focused walkthrough of region importance, mixed-resolution capture, ISP/backend cooperation, localization and classification paths, and the reported evaluation. The authors’ primary manuscript was inspected. Results are author-reported and have not been reproduced here. The pixel, bandwidth, and stopping calculations are original teaching models.',
    'lessons': [('s1', 'Whole-request timing'), ('s2', 'Approximation'), ('s3', 'Movement boundaries'), ('s6', 'Execution plans'), ('s8', 'Accepted behavior'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'Uniform detail spends work where the task may not need it',
            'paragraphs': [
                'A camera pipeline often captures and carries every region at the same resolution. That is safe but wasteful when a small moving object matters and a large flat region does not. The image signal processor, or ISP, already computes clues such as edge density and motion while improving the image. IRIS reuses those clues to decide how much detail each region should keep before the backend receives it.',
                'The decision unit is a region, not the whole frame. IRIS divides the image into a hierarchy of 16×16, 32×32, and 64×64 blocks. It scores the smaller regions, takes the highest score within a larger block, and compares it with a threshold supplied by the application. A low-scoring block can be downsampled; a block containing a high-scoring feature keeps more detail. The backend receives both the pixels and metadata describing each region’s resolution.',
                'Original bandwidth example: a 4,000×2,000 image has 8 million pixels. If 60% of its regions can use one quarter as many pixels and the remaining 40% stay full size, the retained pixel count is 0.60×0.25×8 + 0.40×8 = 4.4 million, a 45% reduction. This assumes the downsampling map and metadata fit within the stated cost; it is not an IRIS measurement.',
            ],
            'sources': [(PDF + '#page=1', 'IRIS paper, abstract and introduction: uniform sampling, ISP byproducts, and mixed-resolution goal'), (PDF + '#page=4', 'IRIS paper, saliency score, hierarchical regions, threshold, and resolution metadata')],
        },
        {
            'title': 'A useful saliency signal must be cheap and match the task',
            'paragraphs': [
                'IRIS combines edge density with perceived motion to form an importance score. Edges suggest boundaries and fine detail; motion suggests a region that may matter to a moving observer or tracker. The backend chooses the threshold, so it can trade image detail for latency and energy according to its task. This makes the score a control signal, not a universal definition of visual importance.',
                'The paper’s co-design matters because computing the same score in software can erase the saving. IRIS adds a saliency scorer, a quad unit, and a downsampling unit inside the ISP path, reusing values the ISP has already produced. The added work is placed so the modeled pipeline does not stall. A software-only version must read the frame, calculate saliency, and then perform the reduction on the backend; its extra delay and memory traffic belong in the comparison.',
                'Original break-even example: saving low-detail processing removes 12 ms and 40 energy units per frame. A software saliency pass costs 5 ms and 18 energy units, leaving 7 ms and 22 units saved. If the pass must also copy the frame for 8 ms and 25 units, the software version loses both measures. A front-end hardware change that reuses existing byproducts can win under this model, but it also requires hardware support that software alone does not provide.',
            ],
            'sources': [(PDF + '#page=3', 'IRIS paper, ISP edge and motion byproducts'), (PDF + '#page=6', 'IRIS paper, hardware units, pipeline integration, and no-stall claim'), (PDF + '#page=11', 'IRIS paper, software-only comparison boundary')],
        },
        {
            'title': 'The backend must change its work, not merely receive smaller images',
            'paragraphs': [
                'Mixed-resolution input changes what a backend algorithm can assume. IRIS uses a mixed-resolution tokenizer for a Vision Transformer so a low-detail region can become a larger-area token without pretending that its pixels have full resolution. For localization, the paper modifies ORB-SLAM3, a visual-tracking and mapping system, to process regions in decreasing importance order and stop when additional regions no longer produce enough new features. The front end’s metadata and the backend’s stopping rule form one system.',
                'This creates two separate acceptance questions. A classifier must retain an acceptable accuracy measure; a localization system must retain an acceptable position error and timely tracking. A frame that is cheap but loses the feature needed for a pose estimate is not an accepted result. Conversely, processing every region to preserve a worst-case guarantee may erase the intended saving.',
                'Original stopping example: four regions provide 40, 25, 8, and 2 new useful features. If the application stops when the next region would add fewer than 5, it processes the first three and obtains 73 features. Processing the last region costs 3 ms for only 2 features, so it is rejected by the rule. If the camera moves and the fourth region now supplies 12 features, the old stopping decision is no longer valid. The threshold must be tied to the current frame and task requirement.',
            ],
            'sources': [(PDF + '#page=8', 'IRIS paper, Vision Transformer mixed-resolution tokenizer'), (PDF + '#page=9', 'IRIS paper, ORB-SLAM3 importance ordering and diminishing-return stopping')],
        },
        {
            'title': 'Read the results with task, baseline, and evidence method attached',
            'paragraphs': [
                'The paper evaluates localization with ORB-SLAM3 on KITTI and classification with a Vision Transformer on ImageNet. It reports, for localization, 22.8% lower average latency, 10.5% lower tail latency, and 22.5% lower energy. For classification it reports 37.5% lower average latency, 9% lower tail latency, and 41.5% lower energy, with less than 1% accuracy loss at a stated threshold. These are separate task results, not one universal vision speedup.',
                'The evidence uses several layers: a modeled ISP and memory system, a cycle-accurate RTL pipeline model for the ISP additions, synthesized 14 nm area and power estimates, and execution on a Jetson AGX Xavier for parts of the pipeline. GPU energy is physically queried while other components are modeled or technology-scaled. A measured GPU number does not turn the combined system estimate into a measured complete SoC, and synthesized area does not establish a taped-out chip.',
                'The paper also reports that software-only saliency can increase latency for small Vision Transformers because the scoring overhead outweighs the saved work. That negative comparison is central to the lesson: the benefit comes from coordinating where the score is produced, where resolution changes, and how the consumer uses the result. This walkthrough has not reproduced the paper’s pipeline, hardware models, or task measurements.',
            ],
            'sources': [(PDF + '#page=2', 'IRIS paper, reported localization/classification reductions and accuracy boundary'), (PDF + '#page=10', 'IRIS paper, evaluation setup, models, baselines, and energy sources'), (PDF + '#page=12', 'IRIS paper, latency, energy, tail, and accuracy results')],
        },
    ],
    'exercise': {
        'question': 'A frame contains 8 million pixels. Suppose 60% of its regions can be reduced to one quarter of their original pixels while 40% remain full size. What fraction of pixels remains? If a software saliency pass costs 5 ms and the saved processing is 12 ms, how much time is saved before any frame-copy cost?',
        'answer': 'The retained pixels are 0.60×0.25×8 + 0.40×8 = 4.4 million, or 55% of the original; the pixel reduction is 45%. The software pass leaves 12 − 5 = 7 ms saved before any copy or metadata cost. These are original teaching numbers, not IRIS measurements; the final comparison still needs task quality, tail latency, and every movement cost.',
    },
}
